from django.urls import path
from . import views

urlpatterns = [
    path('upload/', views.upload_cv, name='upload_cv'),
]