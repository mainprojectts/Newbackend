from django.urls import path
from .views import *

urlpatterns = [
    path("notes/",NoteListcreate.as_view(),name="notes")
]
