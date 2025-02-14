from django.shortcuts import render, redirect
from .forms import CustomUserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages

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
def home(request):
    return render(request, "main/home.html", {})