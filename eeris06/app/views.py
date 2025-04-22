from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponseRedirect, Http404, HttpResponseForbidden, JsonResponse
from django.views.generic.edit import FormView
from django.views.generic import ListView
from django.contrib import messages
from django.utils import timezone
from django.urls import reverse, reverse_lazy
from django.core.mail import send_mail
from decimal import Decimal, ROUND_HALF_UP

import os, json, base64
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from openai import OpenAI

from .forms import CustomUserCreationForm, ReceiptForm, SubmissionForm
from .models import CustomUser, Submission, Receipt

def authUserRegister(request):
    form = CustomUserCreationForm()

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST or None)
        if form.is_valid():
            form.save()
            messages.success(request, "Registration successful! Please login in to proceed.")
            return redirect("app:login")
        else:
            form = CustomUserCreationForm()

    return render(request, 'registration/signup.html', {'form': form})

def authPasswordReset(request):
    if request.method == 'POST':
        email = request.POST.get('username')
        user = CustomUser.objects.filter(email=email).first()
        if user:
            token = user.generate_password_reset_token()
            reset_link = request.build_absolute_uri(reverse('app:authPasswordResetUpdate', args=[token]))
            code =  send_mail(
                        subject=f"EERIS-06 Password Reset - {user.first_name} {user.last_name}",
                        message="Your password reset link will expire in 1 hour. Click the link below to reset your password:\n" + reset_link,
                        from_email=None, # uses Default email address
                        recipient_list=[email],
                   )
            
            if code == 1:
                messages.success(request, "Please check your email for the password reset link.")
            else: 
                messages.warning(request, "There was a problem sending the reset link via email. Please try again later.")

            return redirect("app:login")
        else:
            messages.warning(request, "Email not found!")

    return render(request, 'components/password_reset_email.html')

def authPasswordResetUpdate(request, token):
    user = CustomUser.objects.filter(reset_token=token).first()

    if not user or user.reset_token_expiry < timezone.now():
        messages.warning(request, "Invalid or expired password reset link.")
        return redirect("app:login")

    if request.method == 'POST':
        new_password = request.POST.get('password')
        user.set_password(new_password)
        user.reset_token = None
        user.reset_token_expiry = None
        user.save()
        messages.success(request, "Password reset successfully. Now get back to work!")
        return redirect("app:login")
        
    return render(request, 'components/password_reset_update.html', {'token': token})

@login_required
def editSubmission(request, submission_id=None):

    submission = Submission.objects.get(id=submission_id)

    # Check if the submission has not been approved
    if submission.approved:
        messages.warning(request, "Submission cannot be modified! It has been already approved. Contact your supervisor if needed.")
        return redirect("app:home")

    # Use the Submission's receipt instance for editing
    receipt_instance = submission.receipt

    if request.method == 'POST':
        form = ReceiptForm(request.POST, instance=receipt_instance)
        if form.is_valid():
            form.save()  # Updates the receipt in the database
            messages.success(request, "Submission updated successfully.")
            return redirect("app:home")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        # prefill the form with existing data of the receipt
        form = ReceiptForm(instance=receipt_instance)


    return render(request, 'main/edit_submission.html', { 'form': form, 'submission': submission })

@login_required
def deleteSubmission(request, submission_id=None):
    submission = Submission.objects.get(id=submission_id)

    # Check if the submission has not been approved
    if submission.approved:
        messages.warning(request, "Submission cannot be deleted! It has been already approved. Contact your supervisor if needed.")

    # Delete the submission and its linked receipt
    elif request.method == 'POST':
        receipt_name = submission.receipt.receipt_name
        submission.receipt.delete()  # Deletes the linked receipt
        submission.delete()  # Deletes the submission itself
        messages.success(request, f"Submission {receipt_name} deleted successfully.")
    
    return redirect("app:home")

@login_required
def processSubmission(request, submission_id=None, approve=None):
    if request.method == 'POST' and request.user.is_superuser:
        submission = Submission.objects.get(id=submission_id)

        if submission.processed:
            messages.warning(request, "Submission already processed.")
            return redirect("app:home")
        
        if approve == "true":
            submission.approved = True
            submission.processed = True
            messages.success(request, f"Submission {submission.receipt.receipt_name} approved.")
        elif approve == "false":
            submission.approved = False
            submission.processed = True
            messages.warning(request, f"Submission {submission.receipt.receipt_name} declined.")
        else:
            messages.warning(request, "Invalid action.")

        submission.save()
    else:
        messages.warning(request, "Invalid action. You are not authorized to perform this action.")
        
    return redirect("app:home")

@login_required
def reportAnalytics(request):

    if request.method == 'POST':
        sort_choice = request.POST['choice']
    else:
        sort_choice = 'Total'

    def total(qset):
        return sum([submission.receipt.total_payment for submission in qset])
    
    context = {}
    total_expense, total_approved_expense, total_declined_expense, total_expense_saved = Decimal(0), Decimal(0), Decimal(0), Decimal(0)
    
    if request.user.is_superuser:
        all_submissions = Submission.objects.filter(processed=True)
    else:
        all_submissions = Submission.objects.filter(user=request.user, processed=True)
    
    for category in Receipt.CATEGORY_CHOICES:
        context[category[1]] = {
            'Approved Expenses': total(all_submissions.filter(approved=True, receipt__expense_category=category[0])),
            'Declined Expenses': total(all_submissions.filter(approved=False, receipt__expense_category=category[0])),
        }
        context[category[1]]['Total'] = context[category[1]]['Approved Expenses'] + context[category[1]]['Declined Expenses']
        context[category[1]]['Expense Saved'] = (context[category[1]]['Declined Expenses'] / context[category[1]]['Total'] * 100) if context[category[1]]['Total'] else Decimal(0)
        context[category[1]]['Expense Saved']  = context[category[1]]['Expense Saved'].quantize(Decimal("0.00"), rounding=ROUND_HALF_UP)

        total_expense += context[category[1]]['Total']
        total_approved_expense += context[category[1]]['Approved Expenses']
        total_declined_expense += context[category[1]]['Declined Expenses']

 
    total_expense_saved = (total_declined_expense / total_expense * 100) if total_expense else Decimal(0)
    total_expense_saved = total_expense_saved.quantize(Decimal("0.00"), rounding=ROUND_HALF_UP)

    context = dict(sorted(context.items(), key=lambda item: item[1][sort_choice], reverse=True))
    
    return render(request, 'main/report_analytics.html', {'data':context, 'total_expense': total_expense, 'total_approved_expense': total_approved_expense, 'total_declined_expense': total_declined_expense, 'total_expense_saved': total_expense_saved, 'sort':sort_choice })

@login_required
def employeeDirectory(request):
    employee_list = CustomUser.objects.all().order_by('first_name', 'last_name')
    return render(request, 'main/employee_directory.html', {'employee_list': employee_list})


class HomeView(LoginRequiredMixin, ListView):
    template_name = "main/home.html"
    model = Submission
    login_url = "app:login"

    # filter and sort submission list
    def get_queryset(self):
        return super().get_queryset().filter(created_at__lte=timezone.now()).order_by('-created_at')
    
    # set and pass context to template
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context["receipt_form"] = ReceiptForm()
        context["unapproved_submissions"] = Submission.objects.filter(processed=False) if user.is_superuser else Submission.objects.filter(user=user, processed=False)
        context["approved_submissions"] = Submission.objects.filter(processed=True) if user.is_superuser  else Submission.objects.filter(user=user, processed=True)

        return context


class CreateReceiptView(LoginRequiredMixin, FormView):
    form_class = ReceiptForm
    template_name = "main/home.html"
    success_url = reverse_lazy('app:home')
    login_url = reverse_lazy('app:login')
    redirect_field_name = 'next'

    def form_valid(self, form):
        new_receipt = form.save()

        # Create a submission linked to the receipt
        Submission.objects.create(
            user=self.request.user,
            receipt=new_receipt
        )

        messages.success(self.request, "Receipt successfully created!")
        return HttpResponseRedirect(self.success_url)
    
    def form_invalid(self, form):
        messages.error(self.request, "Please fix the errors below.")

        # Get all submissions to pass them back to the template
        latest_submissions = Submission.objects.filter(
            created_at__lte=timezone.now()
            ).order_by('-created_at')
        
        return self.render_to_response(self.get_context_data(
                receipt_form=form, latest_submissions_list=latest_submissions
                )
            )


class ReceiptExtractView(APIView):
    def post(self, request, *args, **kwargs):
        api_key = settings.OPENAI_API_KEY
        if not api_key:
            return Response(
                {"error": "OpenAI API key is missing or not set."}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        receipt_image = request.FILES.get("image")
        if not receipt_image:
            return Response(
                {"error": "No image file provided."},
                status=status.HTTP_400_BAD_REQUEST
                )
        
        receipt_image_encoded = base64.b64encode(receipt_image.read()).decode('utf-8')
        
        client = OpenAI(api_key=api_key)
        
        openai_file = client.files.create(file=receipt_image.file,purpose="user_data")

        # prepare chat messages
        system_prompt = f"""
        You are a helpful assistant that extracts structured data from receipts.
        Return the extracted data as a JSON object with these fields:
        receipt_name (Format: [store name]-receipt-[number] where number is circled in the top right of the receipt), 
        receipt_date (Format: YYYY-MM-DD), store_name, store_phone (Format: Digits only), store_address,
        store_site (Format: Link to store website), total_payment, pay_method (Format: Choose either Cash, Credit, Debit, Check, E-banking),
        line_items (Format: [Item Quantity] [Item Name] [Item Price]. Only provide price and/or quantity if available. Must be plain text and each item on new line), 
        expense_category. Categories: {', '.join([c for c, _ in Receipt.CATEGORY_CHOICES])}.
        If any field is missing or unreadable, return null.
        Ignore promotions, QR codes, surveys, etc.
        """

        messages = [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Please extract the receipt information from this image."},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{receipt_image.content_type};base64,{receipt_image_encoded}"
                        }
                    }
                ]
            }
        ]

        try:
            completion = client.chat.completions.create(
                messages=messages,
                model="gpt-4.1",
                max_tokens=2000,
                temperature=0.0
            )
            raw = completion.choices[0].message.content.strip()
            payload = json.loads(raw)

        except json.JSONDecodeError:
            return Response(
                {"error": "Invalid JSON output", "raw": raw, "message": "There was a problem loading the data."},
                 status=status.HTTP_502_BAD_GATEWAY
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(payload, status=status.HTTP_200_OK)
