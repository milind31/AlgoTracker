from django import forms
from .models import Signup

class EmailForm(forms.ModelForm):
    class Meta:
        model = Signup
        fields = ('email', 'ticker', 'strategy')

class StockHistoryForm(forms.ModelForm):
    class Meta:
        model = Signup
        fields = ('ticker',)
