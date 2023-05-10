from django.urls import path

from . import views
from .views import OrderSummaryView

urlpatterns = [
    path("", views.index, name="home"),
    path("about", views.about, name="about"),
    path("register", views.register, name="register"),
    path("login", views.login_request, name="login"),
    path("logout", views.logout_request, name="logout"),
    # path('book', views.book_read, name='book'),
    path("book/<int:product_id>/pdf/", views.book_read, name="book_read"),
    path("catalog", views.catalog, name="catalog"),
    path("product/<int:product_id>", views.product, name="product"),
    path("catalog/product/<int:product_id>", views.product, name="product"),
    path("cart", OrderSummaryView.as_view(), name="cart"),
    path("add_to_cart/<int:pk>", views.add_to_cart, name="add_to_cart"),
    path(
        "remove_single_item_from_cart/<int:pk>",
        views.remove_single_item_from_cart,
        name="remove_single_item_from_cart",
    ),
    path("profile", views.profile, name="profile"),
    path("edit_profile_page", views.edit_profile_page, name="edit_profile_page"),
    path("edit_profile", views.edit_profile, name="edit_profile"),
    path("catalog/<str:category>", views.catalog_category, name="catalog_category"),
    path('create_book/', views.create_book, name='create_book'),
    path('search/', views.search, name='search'),
    # path("search/product/<int:product_id>", views.product, name="product"),
    path('product/<int:product_id>/add_review/', views.add_review, name='add_review'),
    path('product/<int:product_id>/delete_review/<int:review_id>/', views.delete_review, name='delete_review'),
]
