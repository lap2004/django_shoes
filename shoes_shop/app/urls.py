from django.contrib import admin
from django.urls import path 
from . import views
urlpatterns = [
    path("", views.home, name="home"),
    path("cart", views.cart, name="cart"),
    path("product/<int:id>/", views.product_detail, name="product_detail"),
    path("checkout", views.checkout, name="checkout"),
    path("order_complete/", views.order_complete, name="order_complete"),
    path("update_item", views.updateItem, name="update_item"),
    path("register", views.register, name="register"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
]
