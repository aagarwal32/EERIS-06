from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponseRedirect, Http404, HttpResponseForbidden, JsonResponse
from django.views.generic.edit import FormView
from django.views.generic import ListView
from django.contrib import messages
from django.utils import timezone
from django.urls import reverse, reverse_lazy

from .forms import CustomUserCreationForm, ReceiptForm, SubmissionForm
from .models import Submission, Receipt

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
        context["unapproved_submissions"] = Submission.objects.filter(approved=False) if user.is_superuser else Submission.objects.filter(user=user, approved=False)
        context["approved_submissions"] = Submission.objects.filter(approved=True) if user.is_superuser  else Submission.objects.filter(user=user, approved=True)

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
