from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import RegexValidator
from django.utils import timezone
from decimal import Decimal
from datetime import datetime, timedelta
import uuid


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractUser):
    username = None  # Remove username field
    email = models.EmailField(unique=True)  # Make email unique
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    reset_token = models.UUIDField(unique=True, null=True, blank=True)
    reset_token_expiry = models.DateTimeField(blank=True, null=True)
 
    objects = CustomUserManager() # Set default custom manager
    
    USERNAME_FIELD = "email"  # Use email to log in
    REQUIRED_FIELDS = ["first_name", "last_name"]  # Required fields besides email

    def __str__(self):
        return self.email
    
    def generate_password_reset_token(self):
        token = uuid.uuid4()
        self.reset_token_expiry = timezone.now() + timedelta(hours=1)
        self.reset_token = token
        self.save(update_fields=["reset_token", "reset_token_expiry"])
        return str(token)



# submission holds user, receipt, and creation date.
class Submission(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="submissions"
    )

    receipt = models.ForeignKey(
        'Receipt', 
        on_delete=models.CASCADE, 
        related_name="submissions",
        null=True,
        blank=True
        )
    
    approved = models.BooleanField(default=False)
    processed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Submission by {self.user.email} on {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}"


def create_default_receipt_name():
    return f"untitled-receipt-{datetime.now().strftime('%Y%m%d%H%M%S')}"

# receipt object
class Receipt(models.Model):
    CATEGORY_CHOICES = [
        ('travel', 'Travel'),
        ('food', 'Food & Drinks'),
        ('office supplies', 'Office Supplies'),
        ('utilities', 'Utilities'),
        ('parking & tolls', 'Parking & Tolls'),
        ('training & workshops', 'Training & Workshops'),
        ('software', 'Software & Subscriptions'),
        ('equipment', 'Equipment Purchases'),
        ('maintenance', 'Maintenance Charges'),
        ('shipping & delivery', 'Shipping & Delivery'),
        ('insurance', 'Insurance'),
        ('marketing', 'Marketing & Advertising'),
        ('events', 'Conferences & Events'),
        ('gifts', 'Client Gifts'),
        ('admin', 'Administrative Fees'),
        ('recruiting', 'Recruiting Expenses'),
        ('employee wellness', 'Employee Wellness & Perks'),
        ('other', 'Other'),
    ]
        
    receipt_name = models.CharField(max_length=50, default=create_default_receipt_name)
    receipt_date = models.DateField(default=timezone.now, help_text="When did you get this receipt?", blank=True)
    store_name = models.CharField(max_length=200)
    
    store_phone = models.CharField(
        max_length=15,
        validators=[RegexValidator(regex=r'^\+?\d{10,15}$', message="Enter a valid phone number.")]
    )
    store_address = models.CharField(max_length=200)
    store_site = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    line_items = models.CharField(max_length=20000, blank=True)
    total_payment = models.DecimalField(max_digits=10, decimal_places=2)
    pay_method = models.CharField(max_length=200)
    expense_category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        default='other',
        blank=False
    )


    def __str__(self):
        return f"Receipt from {self.store_name} - Total: ${self.total_payment}"

