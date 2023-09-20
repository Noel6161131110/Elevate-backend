from django.urls import path 
from . import views

urlpatterns = [
    path('get/stories/', views.ContentBlockView.as_view(), name='content_block')
]