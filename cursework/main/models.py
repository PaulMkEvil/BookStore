from django.conf import settings
from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User


CATEGORY_CHOICES = (
    ("F", "Фэнтези"),
    ("C", "Классика"),
    ("D", "Детектив"),
    ("N", "Новое"),
    ("CH", "Детское"),
    ("O", "Остальное"),
)


class Book(models.Model):
    title = models.CharField("Название", max_length=50)
    category = models.CharField("Категория", choices=CATEGORY_CHOICES, max_length=2)
    author = models.CharField("Автор", max_length=50)
    price = models.FloatField("Цена", default=500)
    description = models.TextField("Описание", max_length=500)
    book_file = models.FileField(upload_to='media/pdfs', default='none')
    book_img = models.FileField(upload_to='static/img', default='none')
    published_date = models.DateField()

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("book", kwargs={"pk": self.pk})

    def get_add_to_cart_url(self):
        return reverse("add_to_cart", kwargs={"pk": self.pk})

    def get_remove_from_cart_url(self):
        return reverse("remove_from_cart", kwargs={"pk": self.pk})


class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField()
    comment = models.TextField(max_length=1000)
    date_added = models.DateTimeField(auto_now_add=True)


class BookItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)
    item = models.ForeignKey(Book, on_delete=models.CASCADE)
    quantity = models.IntegerField("Количество", default=1)

    def __str__(self):
        return self.item.title

    def get_total_item_price(self):
        return self.quantity * self.item.price

    def get_final_price(self):
        return self.get_total_item_price

    def get_quantity(self):
        return self.quantity


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    items = models.ManyToManyField(BookItem)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField()
    ordered = models.BooleanField(default=False)

    def get_total(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_total_item_price()
        return total

    def __str__(self):
        return self.user.username
