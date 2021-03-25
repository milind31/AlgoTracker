from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponseRedirect
from .forms import EmailForm, StockHistoryForm
from .models import Signup
from .yfinance import is_valid_ticker

def email_list_signup(request):
    form = EmailForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            email_signup_qs = Signup.objects.filter(email=form.instance.email, ticker=form.instance.ticker)
            if email_signup_qs.exists():
                messages.error(request, "TICKER ALREADY REGISTERED WITH EMAIL!")
            elif is_valid_ticker(form.instance.ticker) == False:
                messages.error(request, "INVALID TICKER")
                return redirect("main:signup")
            else:
                form.save()
                messages.info(request, "INFO SUCCESSFULLY ADDED!")
        else:
            messages.error(request, "AN ERROR OCCURED, PLEASE MAKE SURE INFORMATION IS FORMATTED CORRECTLY!")
        
        return redirect("main:signup")
    
    form = EmailForm()
    return render(request,
                  "main/signup.html",
                   {"form":form})

def email_list_unsubscribe(request):
    form = EmailForm(request.POST or None)
    if request.method == "POST":
            if form.is_valid():
                email_unsubscribe_qs = Signup.objects.filter(email=form.instance.email, ticker=form.instance.ticker)
                if email_unsubscribe_qs.exists():
                    Signup.objects.filter(email=form.instance.email, ticker=form.instance.ticker).delete()
                    messages.info(request, "INFO SUCCESSFULLY DELETED")
                    return redirect("main:signup")
                else:
                    messages.error(request, "EMAIL/TICKER COMBO DOES NOT EXIST!")
                    return redirect("main:unsubscribe")
            else:
                messages.error(request, "PLEASE MAKE SURE THE EMAIL IS FORMATTED CORRECTLY!")
                return redirect("main:unsubscribe")
        

    form = EmailForm()
    return render(request,
                  "main/unsubscribe.html",
                   {"form":form})

def homepage(request):
    form = StockHistoryForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            if is_valid_ticker(form.instance.ticker) == False:
                messages.error(request, "INVALID TICKER")
                return redirect("main:homepage")
    
    form = StockHistoryForm()
    return render(request,
                  "main/home.html",
                  {'form':form})
