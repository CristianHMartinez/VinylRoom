from django.shortcuts import render, redirect, get_object_or_404
from catalog.models import Genre, Artist, Product, Order, Cart, Tracklist, Address, OrderItem
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, PasswordChangeForm
from .forms import UserRegistrationForm, CustomAuthenticationForm, AddressForm, UserProfileUpdateForm, CustomPasswordChangeForm, SelectAddressForm
from django.core.paginator import Paginator
from django.db.models import Q
import random
import stripe
from django.http import HttpResponse
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django import forms
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from datetime import timedelta
from django.contrib import messages

# Create your views here.
def index(request):
    genre = Genre.objects.all()
    artist = Artist.objects.all()
    genreheader = Genre.objects.all()
    artistheader = Artist.objects.all()

    all_products = list(Product.objects.all())
    product = random.sample(all_products, min(len(all_products), 4))

    return render(request, 'index.html', {
        'genre': genre,
        'artist': artist,
        'product': product, 
        'genreheader': genreheader,
        'artistheader': artistheader,
    })


def product(request, id):
    product = get_object_or_404(Product, id=id)
    
    related_products = Product.objects.filter(artist=product.artist).exclude(id=product.id)

    related_products = list(related_products)
    products = random.sample(related_products, min(len(related_products), 4))

    artists = get_object_or_404(Artist, id=product.artist.id)
    artistheader = Artist.objects.all()
    genreheader = Genre.objects.all()
    tracklist = Tracklist.objects.filter(product=product)

    return render(request, 'product.html', {
        'product': product,
        'products': products,
        'artists': artists,
        'tracklist': tracklist,
        'artistheader': artistheader,
        'genreheader': genreheader
    })


def genre(request, id):
    genre = get_object_or_404(Genre, id=id)
    genreheader = Genre.objects.all()
    products = Product.objects.filter(genre=genre)
    artistheader = Artist.objects.all()

    artist_id = request.GET.get('artist_id')
    price_filter = request.GET.get('price_filter')
    order_by = request.GET.get('order_by')

    if artist_id:
        try:
            artist = get_object_or_404(Artist, id=artist_id)
            products = products.filter(artist=artist)
        except:
            artist = None
    else:
        artist = None

    if price_filter:
        if price_filter == 'lt_500':
            products = products.filter(price__lt=25)
        elif price_filter == 'lt_1000':
            products = products.filter(price__lt=50)
        elif price_filter == 'lt_1500':
            products = products.filter(price__lt=75)
        elif price_filter == 'lt_2000':
            products = products.filter(price__lt=100)

    if order_by == 'price_asc':
        products = products.order_by('price')
    elif order_by == 'price_desc':
        products = products.order_by('-price')
    elif order_by == 'name_asc':
        products = products.order_by('name')
    elif order_by == 'name_desc':
        products = products.order_by('-name')

    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'genre.html', {'genre': genre, 'products': products , 'artist': artist , 'page_obj': page_obj, 'genreheader': genreheader, 'artistheader': artistheader, 'order_by': order_by, 'price_filter': price_filter})

#login and register view
def login_register_view(request):
    login_form = CustomAuthenticationForm(request=request)
    register_form = UserRegistrationForm()
    genreheader = Genre.objects.all()
    artistheader = Artist.objects.all()

    if request.method == 'POST':
        if 'login' in request.POST:
            login_form = CustomAuthenticationForm(request=request, data=request.POST)
            if login_form.is_valid():
                user = login_form.get_user()
                login(request, user)
                return redirect('catalog:index')

        elif 'register' in request.POST:
            register_form = UserRegistrationForm(request.POST)
            if register_form.is_valid():
                register_form.save()
                messages.success(request, 'Account created successfully!')

    return render(request, 'login.html', {
        'login_form': login_form,
        'register_form': register_form,
        'genreheader': genreheader,
        'artistheader': artistheader,
    })


def logout_view(request):
        logout(request)
        return redirect('catalog:index')

def user_profile(request):
    genreheader = Genre.objects.all()
    artistheader = Artist.objects.all()

    if request.user.is_authenticated:
        user = request.user
        orders = Order.objects.filter(user=user).order_by('-order_date').prefetch_related('orderitem_set')
        return render(request, 'profile.html', {
            'user': user,
            'orders': orders,
            'genreheader': genreheader,
            'artistheader': artistheader,
        })
    return redirect('catalog:index')

#delete account view
@login_required
def delete_account(request):
    if request.method == 'POST':
        user = request.user
        user.delete()
        messages.success(request, 'Account deleted successfully!')
        return redirect('catalog:index')
    return redirect('catalog:index')

# Cart view
def cart_view(request):
    genreheader = Genre.objects.all()
    artistheader = Artist.objects.all()

    if not request.user.is_authenticated:
        return redirect('catalog:login_register')

    user = request.user
    cart_items = Cart.objects.filter(user=user)
    total_price = sum(item.product.price * item.quantity for item in cart_items)

    if request.method == 'POST':
        if 'checkout' in request.POST:
            for item in cart_items:
                Order.objects.create(
                    user=user,
                    product=item.product,
                    quantity=item.quantity
                )
                item.delete()
            return redirect('catalog:index')

        elif 'remove' in request.POST:
            item_id = request.POST.get('item_id')
            cart_item = get_object_or_404(Cart, id=item_id, user=user)
            cart_item.delete()
            return redirect('catalog:cart')

        elif 'update' in request.POST:
            item_id = request.POST.get('item_id')
            quantity = request.POST.get('quantity')
            cart_item = get_object_or_404(Cart, id=item_id, user=user)
            cart_item.quantity = quantity
            cart_item.save()
            return redirect('catalog:cart')

        elif 'add' in request.POST:
            product_id = request.POST.get('product_id')
            quantity = int(request.POST.get('quantity', 1))
            product = get_object_or_404(Product, id=product_id)
            cart_item, created = Cart.objects.get_or_create(user=user, product=product)
            if created:
                cart_item.quantity = quantity
            else:
                cart_item.quantity += quantity
            cart_item.save()

            return redirect('catalog:cart')

        elif 'clear_cart' in request.POST:
            cart_items.delete()
            return redirect('catalog:index')

    return render(request, 'cart.html', {
        'cart_items': cart_items,
        'total_price': total_price,
        'genreheader': genreheader,
        'artistheader': artistheader,
    })

#addresses view
@login_required
def manage_addresses(request):
    addresses = Address.objects.filter(user=request.user)
    genreheader = Genre.objects.all()
    artistheader = Artist.objects.all()

    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            new_address = form.save(commit=False)
            new_address.user = request.user
            new_address.save()
            return redirect('catalog:manage_addresses')
    else:
        form = AddressForm()

    return render(request, 'addresses.html', {
        'addresses': addresses,
        'form': form,
        'genreheader': genreheader,
        'artistheader': artistheader,
    })

#delete address view
@login_required
def delete_address(request, address_id):
    address = get_object_or_404(Address, id=address_id, user=request.user)
    if request.method == 'POST':
        address.delete()
        return redirect('catalog:manage_addresses')
    return redirect('catalog:manage_addresses')

#edit address view
@login_required
def edit_address(request, id):
    address = get_object_or_404(Address, id=id, user=request.user)
    genreheader = Genre.objects.all()
    artistheader = Artist.objects.all()

    if request.method == 'POST':
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            form.save()
            # Redirigir a la lista de direcciones después de guardar
            return redirect('catalog:manage_addresses')  # Aquí se cambia a 'manage_addresses'
    else:
        form = AddressForm(instance=address)

    return render(request, 'edit_addresses.html', {
        'form': form,
        'address': address,
        'genreheader': genreheader,
        'artistheader': artistheader,
    })

@login_required
def choose_address_view(request):
    user = request.user
    genreheader = Genre.objects.all()
    artistheader = Artist.objects.all()

    if request.method == 'POST':
        if 'select_address' in request.POST:
            select_form = SelectAddressForm(request.POST, user=user)
            if select_form.is_valid():
                address = select_form.cleaned_data['address']
                request.session['address_id'] = address.id
                return redirect('catalog:checkout')
        elif 'create_address' in request.POST:
            address_form = AddressForm(request.POST)
            if address_form.is_valid():
                address = address_form.save(commit=False)
                address.user = user
                address.save()
                request.session['address_id'] = address.id
                return redirect('catalog:checkout') 
    else:
        select_form = SelectAddressForm(user=user)
        address_form = AddressForm()

    return render(request, 'choose_address.html', {
        'select_form': select_form,
        'address_form': address_form,
        'genreheader': genreheader,
        'artistheader': artistheader,
    })

# User settings view
@login_required
def user_config(request):
    genreheader = Genre.objects.all()
    artistheader = Artist.objects.all()

    if request.method == 'POST':
        profile_form = UserProfileUpdateForm(request.POST, instance=request.user, user=request.user)
        password_form = CustomPasswordChangeForm(request.user, request.POST)

        profile_valid = profile_form.is_valid()
        password_valid = password_form.is_valid()

        if profile_valid:
            profile_form.save()

        if password_valid:
            password_form.save()
            update_session_auth_hash(request, request.user)

        if profile_valid or password_valid:
            return redirect('catalog:user_profile')
    else:
        profile_form = UserProfileUpdateForm(instance=request.user, user=request.user)
        password_form = CustomPasswordChangeForm(request.user)

    return render(request, 'user_config.html', {
        'profile_form': profile_form,
        'password_form': password_form,
        'genreheader': genreheader,
        'artistheader': artistheader,
    })


#Artist view
def artist_view(request, id):
    artist = get_object_or_404(Artist, id=id)
    product = Product.objects.filter(artist=artist)
    genreheader = Genre.objects.all()
    artistheader = Artist.objects.all()

    paginator = Paginator(product, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'artist.html', {
        'artist': artist,
        'product': product,
        'page_obj': page_obj,
        'genreheader': genreheader,
        'artistheader': artistheader,
    })

#catalog view
def catalog_view(request):
    genre_list = Genre.objects.all()
    genreheader = genre_list
    artistheader = Artist.objects.all()

    genre_sections = []

    for genre in genre_list:
        product_ids = list(Product.objects.filter(genre=genre).values_list('id', flat=True))
        random_ids = random.sample(product_ids, min(len(product_ids), 4)) if product_ids else []
        products = Product.objects.filter(id__in=random_ids)
        genre_sections.append((genre, products))

    return render(request, 'catalog.html', {
        'genreheader': genreheader,
        'artistheader': artistheader,
        'genre_sections': genre_sections,
    })


def global_search(request):
    query = request.GET.get('q', '').strip()
    if query:
        product = Product.objects.filter(name__icontains=query).first()
        if product:
            return redirect('catalog:product', id=product.pk)
        
        artist = Artist.objects.filter(name__icontains=query).first()
        if artist:
            return redirect('catalog:artist', id=artist.pk)
    
    return redirect('catalog:product_not_found')


def product_not_found(request):
    return render(request, 'product_not_found.html')

stripe.api_key = settings.STRIPE_SECRET_KEY
YOUR_DOMAIN = settings.YOUR_DOMAIN 

YOUR_DOMAIN = "https://vinylroom-production.up.railway.app/"  # Cambia esto por tu dominio real


def create_checkout_session(request):
    if not request.user.is_authenticated:
        return redirect('catalog:login_register')

    user = request.user
    cart_items = Cart.objects.filter(user=user)

    if not cart_items.exists():
        return HttpResponse("El carrito está vacío.")

    line_items = []
    for item in cart_items:
        if not item.product.stripe_price_id:
            return HttpResponse(f"Producto '{item.product.name}' no tiene un Stripe Price ID configurado.")
        line_items.append({
            'price': item.product.stripe_price_id,
            'quantity': item.quantity,
        })

    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=line_items,
            mode='payment',
            success_url=YOUR_DOMAIN + 'payment-success/',
            cancel_url=YOUR_DOMAIN + 'cancel/',
        )
    except Exception as e:
        return HttpResponse(f"Error al crear la sesión de pago: {str(e)}")

    return redirect(checkout_session.url, code=303)

@login_required
def success_view(request):
    user = request.user
    cart_items = Cart.objects.filter(user=user)

    if not cart_items.exists():
        return redirect('catalog:index')

    address_id = request.session.get('address_id')
    shipping_address = None
    if address_id:
        try:
            shipping_address = Address.objects.get(id=address_id, user=user)
        except Address.DoesNotExist:
            pass  

    def add_business_days(start_date, num_days):
        current = start_date
        added = 0
        while added < num_days:
            current += timedelta(days=1)
            if current.weekday() < 5: 
                added += 1
        return current

    estimated_date = add_business_days(timezone.now().date(), 3)

    order = Order.objects.create(
        user=user,
        shipping_address=shipping_address,
        estimated_delivery=estimated_date
    )

    for item in cart_items:
        OrderItem.objects.create(
            order=order,
            product=item.product,
            quantity=item.quantity,
            price=item.product.price
        )

    cart_items.delete()
    request.session.pop('address_id', None) 
    return render(request, 'success.html', {'order': order})


class UserProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'UserInput', 'placeholder': 'Username'}),
            'email': forms.EmailInput(attrs={'class': 'UserInput', 'placeholder': 'Email'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(UserProfileUpdateForm, self).__init__(*args, **kwargs)

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exclude(pk=self.user.pk).exists():
            raise forms.ValidationError(_('A user with this email already exists.'))
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exclude(pk=self.user.pk).exists():
            raise forms.ValidationError(_('A user with this username already exists.'))
        return username
