from .models import Person,Group,Expense,Settlement         
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class RegisterUser(UserCreationForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user
    
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