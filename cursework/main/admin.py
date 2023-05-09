from django.contrib import admin
from .models import Book, BookItem, Order

# Register your models here.
admin.site.register(Book)
admin.site.register(BookItem)
admin.site.register(Order)
