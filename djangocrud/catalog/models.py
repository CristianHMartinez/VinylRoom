from django.db import models
from django.core.files.uploadedfile import InMemoryUploadedFile
from PIL import Image
from io import BytesIO
import sys
import boto3
from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import post_delete
from django.core.exceptions import ValidationError
import stripe

# This function is used to upload the image to the genres folder in the R2 bucket
def image_file_upload_genre(instance, filename):
    filename = filename.split("-")
    return f'genres/{instance.name}.jpg'

# This function is used to upload the image to the products folder in the R2 bucket
def image_file_upload_product(instance, filename):
    filename = filename.split("-")
    return f'products/{filename}.jpg'

# This function compresses the image and returns it as an InMemoryUploadedFile
def compress_image(image, size_w=None, size_h=None):
    image_temp = Image.open(image)

    if image_temp.mode in ("RGBA", "P"):
        background = Image.new("RGB", image_temp.size, (255, 255, 255))
        background.paste(image_temp, mask=image_temp.split()[3] if image_temp.mode == "RGBA" else None)
        image_temp = background

    original_width, original_height = image_temp.size
    if size_w is None or size_h is None:
        size_w = original_width // 2
        size_h = original_height //2
    
    output_io_stream = BytesIO()
    image_temp = image_temp.resize((size_w, size_h))
    image_temp.save(output_io_stream, format='JPEG', quality=100)
    output_io_stream.seek(0)

    image = InMemoryUploadedFile(
        output_io_stream,
        'ImageField',
        f"{image.name.split('.')[0]}.jpg",
        'image/jpeg',
        sys.getsizeof(output_io_stream),
        None,
    )
    return image

# Create your models here.

#genre model
class Genre(models.Model):
    name = models.CharField(max_length=50)
    image = models.FileField(upload_to=image_file_upload_genre, blank=True, null=True)

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if self.pk:
            existing = Genre.objects.filter(pk=self.pk).first()
            if existing and existing.image == self.image:
                super(Genre, self).save(*args, **kwargs)
                return
        
        if self.image:
            self.image = compress_image(self.image)
        super(Genre, self).save(*args, **kwargs)
    
#product model
class Product(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.FileField(upload_to='products/', blank=True, null=True)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)
    artist = models.ForeignKey('Artist', on_delete=models.CASCADE)
    stock = models.IntegerField(default=0)
    stripe_price_id = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if self.pk:
            existing = Product.objects.filter(pk=self.pk).first()
            if existing and existing.image == self.image:
                super(Product, self).save(*args, **kwargs)
                return
        
        if self.image:
            self.image = compress_image(self.image)
        super(Product, self).save(*args, **kwargs)

#artist model
class Artist(models.Model):
    name = models.CharField(max_length=50)
    image = models.FileField(upload_to='artists/', blank=True, null=True)

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if self.pk:
            existing = Artist.objects.filter(pk=self.pk).first()
            if existing and existing.image == self.image:
                super(Artist, self).save(*args, **kwargs)
                return
        
        if self.image:
            self.image = compress_image(self.image)
        super(Artist, self).save(*args, **kwargs)

#order model
class Order(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    order_date = models.DateTimeField(auto_now_add=True)
    shipping_address = models.ForeignKey('Address', on_delete=models.SET_NULL, null=True, blank=True)
    estimated_delivery = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"Order {self.id} by {self.user.username}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} (Order {self.order.id})"


#cart model
class Cart(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"Cart {self.id} by {self.user.username}"
    
#Tracklist model
class Tracklist(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)
    track_number = models.IntegerField()
    def clean(self):
        if self.product.artist != self.artist:
            raise ValidationError("The product's artist must match the track's artist.")
    class Meta:
        unique_together = ('product', 'track_number')
    track_name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.track_number} - {self.track_name}"
    
#adress model
class Address(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    street_address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.street_address}, {self.city}, {self.state}, {self.zip_code}, {self.country}"

# function to delete image from R2 bucket
# This function is called when the object is deleted
def delete_image_from_r2(instance):
    if instance.image:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.CLOUDFLARE_R2_ACCESS_KEY,
            aws_secret_access_key=settings.CLOUDFLARE_R2_SECRET_KEY,
            endpoint_url=settings.CLOUDFLARE_R2_ENDPOINT
        )
        try:
            s3_client.delete_object(Bucket=settings.CLOUDFLARE_R2_BUCKET, Key=str('media/' + instance.image.name))
            print(f"Deleted {instance.image.name} from R2 bucket")
        except Exception as e:
            print(f"Error deleting {instance.image.name} from R2 bucket: {e}")


#signals to delete image from R2 bucket when the object is deleted
@receiver(post_delete, sender=Genre)
def delete_genre_image(sender, instance, **kwargs):
    delete_image_from_r2(instance)

@receiver(post_delete, sender=Product)
def delete_product_image(sender, instance, **kwargs):
    delete_image_from_r2(instance)

@receiver(post_delete, sender=Artist)
def delete_artist_image(sender, instance, **kwargs):
    delete_image_from_r2(instance)