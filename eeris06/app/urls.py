from django.urls import path, include
from . import views

# define application namespace
app_name = 'app'

urlpatterns = [
    path('', views.HomeView.as_view(), name="home"),
    path('receipt/', views.CreateReceiptView.as_view(), name="create_receipt"),
    path('receipt/extract/', views.ReceiptExtractView.as_view(), name="extract_receipt"),
    path('accounts/', include('django.contrib.auth.urls')),
    path('register/', views.authUserRegister, name='authUserRegister'),
    path('reset/', views.authPasswordReset, name='authPasswordReset'),
    path('password-update/<token>/', views.authPasswordResetUpdate, name='authPasswordResetUpdate'),
    path('edit/<int:submission_id>', views.editSubmission, name='editSubmission'),
    path('delete/<int:submission_id>', views.deleteSubmission, name='deleteSubmission'),
    path('process/<int:submission_id>/<str:approve>', views.processSubmission, name='processSubmission'),
    path('report-analytics/', views.reportAnalytics, name='reportAnalytics'),
    path('employee-directory/', views.employeeDirectory, name='employeeDirectory'),
]
