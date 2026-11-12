from django import forms
from .models import FinancialDetail

class FinancialDetailForm(forms.ModelForm):
    class Meta:
        model = FinancialDetail
        fields = ['income', 'expenses', 'savings', 'debts']
        widgets = {
            'income': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'expenses': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'savings': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'debts': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }