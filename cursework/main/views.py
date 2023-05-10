import django.utils.timezone as timezone
from django.shortcuts import render
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import user_passes_test
from django.views import View
from django.db.models import Q
import pdfkit
import mimetypes
import os

from django.conf import settings
from django.http import HttpResponse

from .models import Book, BookItem, Review, Order
from .forms import BookForm


def index(request):
    books = Book.objects.all()
    return render(request, "main/index.html", {"books": books})


def about(request):
    return render(request, "main/about.html")


def book_read(request, product_id):
    # Получите ссылку на PDF из модели
    book = Book.objects.get(id=product_id)

    # Укажите путь к папке, где хранятся PDF-файлы
    file_path = book.book_file.path

    # Проверьте, существует ли файл PDF
    if os.path.exists(file_path):
        with open(file_path, 'rb') as f:
            # Определите тип содержимого файла
            content_type, _ = mimetypes.guess_type(file_path)
            response = HttpResponse(f.read(), content_type=content_type)
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
            return response

    # Если файл PDF не найден, верните 404 ошибку или другую обработку ошибки
    return HttpResponse('PDF not found', status=404)

def search(request):
    query = request.GET.get('q')
    if query:
        books = Book.objects.filter(
            Q(title__icontains=query) | Q(author__icontains=query)
        )
    else:
        books = Book.objects.all()
    return render(request, 'main/search_results.html', {'books': books, 'query': query})

@user_passes_test(lambda u: u.is_superuser)
def create_book(request):
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('catalog')  # Перенаправьте пользователя на страницу списка книг
    else:
        form = BookForm()
    return render(request, 'main/create_book.html', {'form': form})


def catalog(request):
    categories = [
        {"name": "Всё", "link": "/catalog", "id": ""},
        {"name": "Фэнтези", "link": "/catalog/F", "id": "F"},
        {"name": "Классика", "link": "/catalog/C", "id": "C"},
        {"name": "Детектив", "link": "/catalog/D", "id": "D"},
        {"name": "Новое", "link": "/catalog/N", "id": "N"},
        {"name": "Детское", "link": "/catalog/CH", "id": "CH"},
        {"name": "Остальное", "link": "/catalog/O", "id": "O"},
    ]
    category = ""
    products = Book.objects.all()
    context = {"products": products, "categories": categories, "category": category}
    return render(request, "main/catalog.html", context=context)


def product(request, product_id):
    product = Book.objects.get(id=product_id)
    context = {"product": product}
    return render(request, "main/book.html", context=context)


def login_request(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            return redirect("home")
        else:
            return redirect("login")
    return render(request, "main/login.html")


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password1 = request.POST["password1"]
        password2 = request.POST["password2"]
        first_name = request.POST["first_name"]
        last_name = request.POST["last_name"]

        if password1 == password2:
            if auth.models.User.objects.filter(username=username).exists():
                return redirect("register")
            elif auth.models.User.objects.filter(email=email).exists():
                return redirect("register")
            else:
                user = auth.models.User.objects.create_user(
                    username=username,
                    email=email,
                    password=password1,
                    first_name=first_name,
                    last_name=last_name,
                )
                user.save()
                user = auth.authenticate(username=username, password=password1)
                auth.login(request, user)
                return redirect("home")
        else:
            return redirect("register")
    return render(request, "main/register.html")


class OrderSummaryView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {"object": order}
            return render(self.request, "main/cart.html", context)
        except ObjectDoesNotExist:
            return redirect("/")


@login_required
def add_to_cart(request, pk):
    product = Book.objects.get(id=pk)
    order_item, created = BookItem.objects.get_or_create(
        item=product,
        user=request.user,
        ordered=False,
    )
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(item__id=pk).exists():
            order_item.quantity = 1
            order_item.save()
            return redirect("cart")
        else:
            order.items.add(order_item)
            return redirect("cart")
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(
            user=request.user,
            ordered_date=ordered_date,
        )
        order.items.add(order_item)
        return redirect("cart")


@login_required
def remove_single_item_from_cart(request, pk):
    item = get_object_or_404(Book, id=pk)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(item__pk=item.pk).exists():
            order_item = BookItem.objects.filter(
                item=item, user=request.user, ordered=False
            )[0]
            order.items.remove(order_item)
            return redirect("cart")
        else:
            return redirect("book", pk=pk)
    else:
        return redirect("book", pk=pk)


@login_required
def logout_request(request):
    logout(request)
    return redirect("home")


@login_required
def profile(request):
    return render(
        request,
        "main/profile.html",
    )


@login_required
def edit_profile_page(request):
    user = request.user
    context = {"user": user}
    return render(request, "main/edit_profile.html", context=context)


@login_required
def edit_profile(request):
    user = auth.models.User.objects.get(username=request.user)
    username = request.user
    if request.method == "POST":
        email = request.POST["email"]
        first_name = request.POST["first_name"]
        last_name = request.POST["last_name"]
        password1 = request.POST["password1"]
        password2 = request.POST["password2"]

        if password1 == password2:
            user.email = email
            user.first_name = first_name
            user.last_name = last_name
            user.save()
            user = auth.authenticate(username=username, password=password1)
            auth.login(request, user)
            return redirect("profile")
    return render(request, "main/edit_profile.html")


def catalog_category(request, category):
    categories = [
        {"name": "Всё", "link": "/catalog", "id": ""},
        {"name": "Фэнтези", "link": "/catalog/F", "id": "F"},
        {"name": "Классика", "link": "/catalog/C", "id": "C"},
        {"name": "Детектив", "link": "/catalog/D", "id": "D"},
        {"name": "Новое", "link": "/catalog/N", "id": "N"},
        {"name": "Детское", "link": "/catalog/CH", "id": "CH"},
        {"name": "Остальное", "link": "/catalog/O", "id": "O"},
    ]
    products = Book.objects.filter(category=category)
    context = {"products": products, "category": category, "categories": categories}
    return render(request, "main/catalog.html", context=context)
