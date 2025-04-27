from django.urls import path
from . import views

app_name = 'catalog'

urlpatterns = [
    path('', views.index, name='index'),
    path('product/<int:id>/', views.product, name='product'),
    path('genre/<int:id>/', views.genre, name='genre'),
    path('login/', views.login_register_view, name='login_register'),
    path('user_profile/', views.user_profile, name='user_profile'),
    path('logout/', views.logout_view, name='logout'),
    path('cart/', views.cart_view, name='cart'),
    path('profile/', views.user_config, name='user_config'),
    path('addresses/', views.manage_addresses, name='manage_addresses'),
    path('edit-address/<int:id>/', views.edit_address, name='edit_address'),
    path('artist/<int:id>/', views.artist_view, name='artist'),
    path('catalog/', views.catalog_view, name='catalog'),
    path('checkout/', views.create_checkout_session, name='checkout'),
    path('payment-success/', views.success_view, name='success'),
    path('search/', views.global_search, name='global_search'),
    path('product-not-found/', views.product_not_found, name='product_not_found'),
    path('chose-address/', views.choose_address_view, name='choose_address'),
    path('addresses/delete/<int:address_id>/', views.delete_address, name='delete_address'),
    path('delete-account/', views.delete_account, name='delete_account'),
    
]
