from django.urls import path, include
from . import views

# define application namespace
app_name = 'app'

urlpatterns = [
    path('', views.HomeView.as_view(), name="home"),
    path('receipt/', views.CreateReceiptView.as_view(), name="create_receipt"),
    path('accounts/', include('django.contrib.auth.urls')),
    path('register/', views.authUserRegister, name='authUserRegister'),
    path('edit/<int:submission_id>', views.editSubmission, name='editSubmission'),
]
