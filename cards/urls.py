from django.urls import path
from . import views

urlpatterns = [
    path("upload/", views.upload_view, name="upload"),
    path("cards/<int:pk>/", views.card_detail_view, name="card_detail"),
]