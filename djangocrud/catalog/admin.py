from django.contrib import admin

# Register your models here.
from .models import Genre
from .models import Product
from .models import Artist
from .models import Tracklist
from .models import Order
from .models import Cart

admin.site.register(Genre)
admin.site.register(Product)
admin.site.register(Artist)
admin.site.register(Tracklist)
admin.site.register(Order)
admin.site.register(Cart)

