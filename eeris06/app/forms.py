from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Submission, Receipt

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ["email", "first_name", "last_name", "password1", "password2"]  


class SubmissionForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ["receipt"]


class ReceiptForm(forms.ModelForm):
    class Meta:
        model = Receipt
        fields = ["receipt_name", "store_name", "store_phone", "store_address", "store_site", "line_items", "total_payment", "pay_method", "expense_category"]

        labels = {
            "receipt_name": "Receipt Name",
            "store_name": "Store Name",
            "store_phone": "Store Phone",
            "store_address": "Store Address",
            "store_site": "Store Website",
            "line_items": "Line Items Description",
            "total_payment": "Total Payment",
            "pay_method": "Payment Method",
            "expense_category": "Expense Category",
        }
        
        widgets = {
            'receipt_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter receipt name (e.g., walmart-receipt-01)'}),
            'store_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter store name (e.g., walmart)'}),
            'store_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter store phone number (e.g., 1234567890)'}),
            'store_address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter store address (e.g., Land O Lakes Blvd, Lutz, FL 33549)'}),
            'store_site': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Enter store website (optional)'}),
            'line_items': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter description of line items (optional)\n(e.g., item 1: Coffee Mug, quantity: 2, price: $8.99 \nitem 2: Watch, quantity: 1, price: $20.99)', 'rows': 3}),
            'total_payment': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter total payment amount (e.g., 29.98)'}),
            'pay_method': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter payment method (e.g., Credit Card, Cash)'}),
            'expense_category': forms.Select(attrs={'class': 'form-control',      'style': 'overflow-y: auto;', 'onfocus': 'this.size=5;', 'onblur': 'this.size=1;', 'onchange': 'this.size=1; this.blur();',}),
        }
