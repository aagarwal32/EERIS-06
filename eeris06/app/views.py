from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages

def authUserRegister(request):
    form = UserCreationForm()

    if request.method == 'POST':
        form = UserCreationForm(request.POST or None)
        if form.is_valid():
            form.save()
            messages.success(request, "Registration successful! Please login in to proceed.")
            return redirect("app:login")
        else:
            form = UserCreationForm()

    return render(request, 'registration/signup.html', {'form': form})

@login_required
def home(request):
    return render(request, "main/home.html", {})