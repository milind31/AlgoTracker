from django import forms
from .models import Signup

#email signups
class EmailForm(forms.ModelForm):
    class Meta:
        model = Signup
        fields = ('email', 'ticker', 'strategy')

#view performance on stock form
class StockHistoryForm(forms.ModelForm):
    class Meta:
        model = Signup
        fields = ('ticker',)
