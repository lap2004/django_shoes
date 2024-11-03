from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from app.templatetags.custom_filters import register
from .models import *
import json
from django.contrib import messages
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.conf import settings
import stripe
from .models import Order, ShippingAddress

stripe.api_key = settings.STRIPE_TEST_SECRET_KEY

def home(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        items = []
        order = {"get_cart_total": 0, "get_cart_items": 0}
        cartItems = order["get_cart_items"]
    products = Product.objects.all()
    context = {"products": products, "cartItems": cartItems}
    return render(request, "app/home.html", context)


def product_detail(request, id):
    product = Product.objects.get(id=id)
    context = {"product": product}
    return render(request, "app/detail.html", context)


def cart(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        items = []
        order = {"get_cart_total": 0, "get_cart_items": 0}
        cartItems = order["get_cart_items"]
    contex = {"items": items, "order": order, "cartItems": cartItems}
    return render(request, "app/cart.html", contex)


def checkout(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        items = []
        order = {"get_cart_total": 0, "get_cart_items": 0}
        cartItems = order["get_cart_items"]

    if request.method == "POST":
        address = request.POST.get("address")
        city = request.POST.get("city")
        state = "pending"
        mobile = request.POST.get("mobile")

        # Lưu thông tin địa chỉ giao hàng
        shipping_address = ShippingAddress(
            customer=customer,
            order=order,
            address=address,
            city=city,
            state=state,
            mobile=mobile,
        )
        shipping_address.save()

        # Đánh dấu đơn hàng là đã hoàn tất
        order.complete = True
        order.save()

        return redirect("order_complete")  # Điều hướng đến trang hoàn tất đơn hàng

    context = {"items": items, "order": order, "cartItems": cartItems}
    return render(request, "app/checkout.html", context)


def order_complete(request):
    return render(request, "app/thankyou.html")

def updateItem(request):
    try:
        data = json.loads(request.body)
        productId = data["productId"]
        action = data["action"]
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON data"}, status=400)
    customer = request.user.customer
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

    if action == "add":
        orderItem.quantity += 1
    elif action == "remove":
        orderItem.quantity -= 1

    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse("Item was added", safe=False)


class CustomUserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label="Mật khẩu", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Xác nhận mật khẩu", widget=forms.PasswordInput)
    name = forms.CharField(max_length=200, required=True)

    class Meta:
        model = User
        fields = ("username", "email")  # Trường name không nên ở đây

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Mật khẩu không khớp")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user
def register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False) 
            user.save() 

            # Lưu Customer
            name = form.cleaned_data["name"]
            customer = Customer(user=user, name=name, email=form.cleaned_data["email"])
            customer.save()

            return redirect("login")
    else:
        form = CustomUserCreationForm()

    # Trả về form (đảm bảo trả về đối tượng HttpResponse)
    return render(request, "app/register.html", {"form": form})
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect(
                "home"
            )
        else:
            error_message = "Tên đăng nhập hoặc mật khẩu không đúng."
            return render(request, "app/login.html", {"error_message": error_message})

    return render(request, "app/login.html")
def logout_view(request):
    logout(request)
    return redirect("login")
