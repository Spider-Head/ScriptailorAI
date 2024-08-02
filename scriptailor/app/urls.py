from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('flask/', views.flask_proxy, name='flask_proxy'),
    
]
