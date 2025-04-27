# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Product
from django.conf import settings
import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY

@receiver(post_save, sender=Product)
def create_stripe_price(sender, instance, created, **kwargs):
    if not instance.stripe_price_id:
        try:
            # Crea el producto en Stripe (opcional, si aún no tienes uno por cada producto)
            stripe_product = stripe.Product.create(name=instance.name)

            # Crea el precio en Stripe
            stripe_price = stripe.Price.create(
                product=stripe_product.id,
                unit_amount=int(instance.price * 100),  # Stripe usa centavos
                currency="usd",  # Cambia a tu moneda si es necesario
            )

            # Guarda el ID de Stripe en el producto
            instance.stripe_price_id = stripe_price.id
            instance.save()
        except Exception as e:
            print(f"Error creando precio en Stripe: {e}")
