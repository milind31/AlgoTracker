from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.core.mail import send_mail
from .forms import EmailForm, StockHistoryForm
from .models import Signup
from .yfinance import is_valid_ticker
from .plots import get_plots
from .emails import send_email

def email_list_signup(request):
    form = EmailForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            email_signup_qs = Signup.objects.filter(email=form.instance.email, ticker=form.instance.ticker, strategy=form.instance.strategy)
            if email_signup_qs.exists():
                messages.error(request, "TICKER/STRATEGY ALREADY REGISTERED WITH EMAIL!")
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
                email_unsubscribe_qs = Signup.objects.filter(email=form.instance.email, ticker=form.instance.ticker, strategy=form.instance.strategy)
                if email_unsubscribe_qs.exists():
                    Signup.objects.filter(email=form.instance.email, ticker=form.instance.ticker, strategy=form.instance.strategy).delete()
                    messages.info(request, "INFO SUCCESSFULLY DELETED")
                    return redirect("main:unsubscribe")
                else:
                    messages.error(request, "EMAIL/TICKER/STRATEGY COMBO DOES NOT EXIST!")
                    return redirect("main:unsubscribe")
            else:
                messages.error(request, "PLEASE MAKE SURE THE EMAIL IS FORMATTED CORRECTLY!")
                return redirect("main:unsubscribe")
        

    form = EmailForm()
    return render(request,
                  "main/unsubscribe.html",
                   {"form":form})

def atrlimitorder(request):
    form = StockHistoryForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            if is_valid_ticker(form.instance.ticker) == False:
                messages.error(request, "INVALID TICKER")
                return redirect("main:atrlimitorder")
            else:
                buy_sell_graph, gain_loss_graph, total_cash_graph, total_cash_buy_hold_graph = get_plots(form.instance.ticker, 'ATR')
                return render(request,
                              "main/strategies/atrlimitorder/atrlimitorderplots.html",
                              {'form':form, 'buy_sell_graph':buy_sell_graph, 'gain_loss_graph':gain_loss_graph, 'total_cash_graph':total_cash_graph, 'total_cash_buy_hold_graph':total_cash_buy_hold_graph})
                
    form = StockHistoryForm()
    return render(request,
                  "main/strategies/atrlimitorder/atrlimitorder.html",
                  {'form':form})


def goldencross(request):
    form = StockHistoryForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            if is_valid_ticker(form.instance.ticker) == False:
                messages.error(request, "INVALID TICKER")
                return redirect("main:goldencross")
            else:
                buy_sell_graph, gain_loss_graph, total_cash_graph, total_cash_buy_hold_graph = get_plots(form.instance.ticker, 'GC')
                return render(request,
                              "main/strategies/goldencross/goldencrossplots.html",
                              {'form':form, 'buy_sell_graph':buy_sell_graph, 'gain_loss_graph':gain_loss_graph, 'total_cash_graph':total_cash_graph, 'total_cash_buy_hold_graph':total_cash_buy_hold_graph})
                
    form = StockHistoryForm()
    return render(request,
                  "main/strategies/goldencross/goldencross.html",
                  {'form':form})

def home(request):
    send_email('vaweh87704@dwgtcm.com', 'QQQ', 'GC')
    return render(request,
                  "main/strategies.html")

