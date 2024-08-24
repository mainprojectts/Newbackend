from django.urls import path
from .views import *

urlpatterns = [
    path("notes/",NoteListcreate.as_view(),name="notes"),
    path("product/",ProductView.as_view(),name="product"),
    path("cart/",CartView.as_view(),name="cart"),
]
