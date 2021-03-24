from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponseRedirect
from .forms import EmailForm
from .models import Signup

def email_list_signup(request):
    form = EmailForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            email_signup_qs = Signup.objects.filter(email=form.instance.email)
            if email_signup_qs.exists():
                messages.error(request, "EMAIL ALREADY EXISTS!")
            else:
                form.save()
                messages.info(request, "EMAIL SUCCESSFULLY ADDED!")
        else:
            messages.error(request, "AN ERROR OCCURED, PLEASE MAKE SURE THE EMAIL IS FORMATTED CORRECTLY!")
        
        return redirect("main:signup")
    
    form = EmailForm()
    return render(request,
                  "main/signup.html",
                   {"form":form})

def email_list_unsubscribe(request):
    form = EmailForm(request.POST or None)
    if request.method == "POST":
            if form.is_valid():
                email_unsubscribe_qs = Signup.objects.filter(email=form.instance.email)
                if email_unsubscribe_qs.exists():
                    Signup.objects.filter(email=form.instance.email).delete()
                    messages.info(request, "EMAIL SUCCESSFULLY DELETED")
                else:
                    messages.error(request, "EMAIL DOES NOT EXIST!")
            else:
                messages.error(request, "PLEASE MAKE SURE THE EMAIL IS FORMATTED CORRECTLY!")
            
            return redirect("main:unsubscribe")

    form = EmailForm()
    return render(request,
                  "main/unsubscribe.html",
                   {"form":form})