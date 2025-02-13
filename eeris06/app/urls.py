from django.urls import path, include
from . import views

# define application namespace
app_name = 'app'

urlpatterns = [
    path('accounts/', include('django.contrib.auth.urls')),
]
