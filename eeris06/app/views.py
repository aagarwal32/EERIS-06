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


class HomeView(LoginRequiredMixin, ListView):
    template_name = "main/home.html"
    context_object_name = "latest_submissions_list"
    model = Submission
    login_url = "app:login"

    # filter and sort submission list
    def get_queryset(self):
        return super().get_queryset().filter(created_at__lte=timezone.now()).order_by('-created_at')
    
    # set and pass context to template
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['receipt_form'] = ReceiptForm()
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
