from django import forms
from .models import Book, Review


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'category', 'author', 'price', 'description', 'book_file', 'book_img', 'published_date']


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ('rating', 'comment')
        labels = {
            'rating': 'Рейтинг (от 1 до 5)',
            'comment': 'Комментарий'
        }
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 5})
        }
