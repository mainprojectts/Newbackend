from django.urls import path
from .views import *

urlpatterns = [
    path("notes/",NoteListcreate.as_view(),name="notes"),
    path("product/",ProductView.as_view(),name="product"),
    path("cart/",CartView.as_view(),name="cart"),
    path("wishlist/",Wishlistview.as_view(),name="wishlist"),
    path("googlelogin/",googleLogin.as_view(),name="googlelogin"),
    path("githublogin/",Githublogin.as_view(),name="githublogin"),
    # path("user/",GetuserDetailview.as_view(),name="user")
]
