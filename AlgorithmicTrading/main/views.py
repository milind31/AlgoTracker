from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.core.mail import send_mail
from .forms import EmailForm, StockHistoryForm
from .models import Signup
from .yfinance import is_valid_ticker
from .plots import get_plots
from .sendgrid import send_email

def email_list_helper(request, strategy):
    form = EmailForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            if strategy != "":
                email_signup_qs = Signup.objects.filter(email=form.instance.email, ticker=form.instance.ticker, strategy=strategy)
            else:
                email_signup_qs = Signup.objects.filter(email=form.instance.email, ticker=form.instance.ticker)
                
            if email_signup_qs.exists():
                messages.error(request, "TICKER/STRATEGY ALREADY REGISTERED WITH EMAIL!")
            elif is_valid_ticker(form.instance.ticker) == False:
                messages.error(request, "INVALID TICKER")
                return redirect("main:signup")
            else:
                form.save()
                messages.info(request, "INFO SUCCESSFULLY ADDED! CHECK EMAIL FOR CONFIRMATION MESSAGE")

                #send confirmation email message
                strategy_dict = {'GC' : 'Golden Cross', 'ATR' : 'ATR Limit Order'}
                email_text = 'This message was sent to confirm that you signed up to be notified when the ' + str(strategy_dict[form.instance.strategy]) + ' strategy executes a trade on ' + str(form.instance.ticker) + '.'
                send_email(str(form.instance.email), 'AlgoTracker Subscription Confirmation', email_text)
        else:
            messages.error(request, "AN ERROR OCCURED, PLEASE MAKE SURE INFORMATION IS FORMATTED CORRECTLY!")
        
        return redirect("main:signup")

#signup page
def email_list_signup(request):
    email_list_helper(request,"")
    form = EmailForm()
    return render(request,
                  "main/signup.html",
                   {"form":form})

#sign up to particular strategy
def email_list_strategy_signup(request, strategy):
    email_list_helper(request,strategy)
    form = EmailForm()
    if strategy:
        form['strategy'].initial = strategy
    return render(request,
                  "main/signup.html",
                   {"form":form})

#unsubscribe page
def email_list_unsubscribe(request):
    form = EmailForm(request.POST or None)
    if request.method == "POST":
            if form.is_valid():
                email_unsubscribe_qs = Signup.objects.filter(email=form.instance.email, ticker=form.instance.ticker, strategy=form.instance.strategy)
                if email_unsubscribe_qs.exists():
                    Signup.objects.filter(email=form.instance.email, ticker=form.instance.ticker, strategy=form.instance.strategy).delete()
                    messages.info(request, "INFO SUCCESSFULLY DELETED! CHECK EMAIL FOR CONFIRMATION MESSAGE")

                    #send confirmation email message
                    strategy_dict = {'GC' : 'Golden Cross', 'ATR' : 'ATR Limit Order'}
                    email_text = 'This message was sent to confirm that you would no longer like to be notified when the ' + str(strategy_dict[form.instance.strategy]) + ' strategy executes a trade on ' + str(form.instance.ticker) + '.'
                    send_email(str(form.instance.email), 'AlgoTracker Unsubscription Confirmation', email_text)

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

#atr page
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

#gc page
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

def strategies(request):
    return render(request,
                  "main/strategies.html")

def home(request):
    return render(request,
                  "main/homepage.html")
