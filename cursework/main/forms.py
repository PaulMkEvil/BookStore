from django import forms
from .models import Book

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'category', 'author', 'description', 'book_file', 'published_date']
