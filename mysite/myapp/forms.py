from .models import Person,Group,Expense,Settlement         
from django import forms
from django.contrib.auth.models import User

class RegisterUser(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username','email','password',)

# could not understand
class CreateGroup(forms.ModelForm):
    class Meta:
        model = Group
        fields = ('groupName','members','made_by',)

class AddExpense(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ('expenseName','description','payer','amount','group')

class SettlementForm(forms.ModelForm):
    class Meta:
        model = Settlement
        fields = ('payer','payee','amount')