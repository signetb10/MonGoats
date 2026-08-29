from django.urls import path

from . import views

urlpatterns = [
    path("", views.home_view, name="home"),
    path("about/", views.about_view, name="about"),
    path("upload/", views.upload_view, name="upload"),
    path("cards/<int:pk>/", views.card_detail_view, name="card_detail"),
]
