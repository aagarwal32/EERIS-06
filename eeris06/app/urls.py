from django.urls import path, include
from . import views

# define application namespace
app_name = 'app'

urlpatterns = [
    path('', views.home, name="home"),
    path('accounts/', include('django.contrib.auth.urls')),
    path('register/', views.authUserRegister, name='authUserRegister'),
]
