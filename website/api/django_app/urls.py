from django.urls import path
from api.django_app import views

urlpatterns = [
    path("api/recommend/", view=views.recommend_view, name="recommend")
]