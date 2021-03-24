from django.shortcuts import render
from django.contrib import messages
from django.http import HttpResponseRedirect
from .forms import EmailSignupForm
from .models import Signup

def email_list_signup(request):
    form = EmailSignupForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            email_signup_qs = Signup.objects.filter(email=form.instance.email)
            if email_signup_qs.exists():
                messages.info(request, "EMAIL ALREADY EXISTS")
            else:
                form.save()
        
        return render(request, 'main/home.html', {"form":form})
    
    form = EmailSignupForm()
    return render(request,
                  "main/home.html",
                   {"form":form})