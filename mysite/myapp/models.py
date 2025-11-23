from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator

# Create your models here.
class Person(models.Model):    
    name = models.CharField(max_length=100,null=True,blank=True)
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    image = models.ImageField(upload_to='static/images/users',default='static/images/uses/default-1.png') 

    def __str__(self):
        return self.name

class Group(models.Model):
    groupName = models.CharField(max_length=100,unique=True)
    made_by = models.ForeignKey(Person,on_delete=models.CASCADE,related_name="Group_creator")
    members = models.ManyToManyField(Person,related_name="group_members")

    def __str__(self):
        return self.groupName
    
class Expense(models.Model):
    expenseName = models.CharField(max_length=100,default='item')
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    description = models.TextField(default=None,blank=True)
    payer = models.ForeignKey(Person,on_delete=models.CASCADE)
    group = models.ForeignKey(Group,on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now=True)
    image = models.ImageField(default='static/images/uses/default-1.png')

    def __str__(self):
        return self.expenseName
    
    def clean(self):
        error = {}

        if self.amount <=0:
            error['amount'] = f'Expense Value Cannot be Negative or Zero'
        
        if self.payer not in self.group.members.all():
            error['payer'] = f'The {self.payer.name} is not in {self.group.groupName}'

        if error:
            raise ValidationError(error)

    def save(self,*args,**kwargs):
        self.full_clean()
        return super().save()

class ExpenseShare(models.Model):
    SPLIT_TYPE = [
    ('equal', 'Equal'),
    ('unequal', 'Unequal'),  
    ('percent', 'Percentage'),
    ]
    expsAmount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    expsPerson = models.ForeignKey(Person,on_delete=models.CASCADE)
    expense = models.ForeignKey(Expense,on_delete=models.CASCADE)
    splitType = models.CharField(
        max_length=50,
        default='equal',
        choices=SPLIT_TYPE
        )

   
    def clean(self):
        error = {}

        if self.expsAmount <=0:
            error['amount'] = f'Expense Value Cannot be Negative or Zero'
        
        if self.expsPerson not in self.expense.group.members.all():
            error['payer'] = f'The {self.payer.name} is not in {self.group.groupName}'

        if error:
            raise ValidationError(error)
    

    def __str__(self):
        return  self.expsPerson.name + ' shares ' + str(self.expsAmount) +  ' in ' + self.expense.expenseName +"Of " + self.expense.group.groupName
  
    def save(self,*args,**kwargs):
        self.full_clean()
        return super().save()

class Settlement(models.Model):
    payer = models.ForeignKey(Person,on_delete=models.CASCADE,related_name='amount_payer')
    payee = models.ForeignKey(Person,on_delete=models.CASCADE,related_name='amount_receiver')
    date = models.DateTimeField(auto_now=True)
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    group = models.ForeignKey(Group,on_delete=models.CASCADE)

    def __str__(self):
        return str(self.payer) + ' paid '+ str(self.payee) + ' on ' + str(self.date.date())

    def clean(self):
        if self.payee.id == self.payer.id:
            raise ValidationError('Payer and Payee should not be same')
        elif self.amount<=0.0:
            raise ValidationError('Amount could not be 0.0')

    def save(self,*args,**kwargs):
        self.full_clean()
        return super().save()
    
    
class Balance(models.Model):
    person = models.ForeignKey(Person,on_delete=models.CASCADE,related_name="owing_person")
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )
    updated_on = models.DateTimeField(auto_now=True)
    group = models.ForeignKey(Group,on_delete=models.CASCADE)
    rPerson  = models.ForeignKey(Person,on_delete=models.CASCADE,related_name="receive_person",default=2)
    def __str__(self):
        return str(self.person) + ' has balance ' + str(self.amount) +' with ' + self.rPerson.name + ' in ' + self.group.groupName
    
    def clean(self):
        if self.person == self.rPerson:
            raise ValidationError('Person and rPerson should not be same')
        
        members = self.group.members.all()

        if self.person not in members :
            raise ValidationError(f'{self.person} not in the {self.group}')
        
        if self.rPerson not in members:
            raise ValidationError(f'{self.rPerson} not in the {self.group}')

    def save(self,*args,**kwargs):
        self.full_clean()
        return super().save()
   

class SettleTran(models.Model):
    balance = models.ForeignKey(Balance,on_delete=models.CASCADE)
    settlement = models.ForeignKey(Settlement,on_delete=models.CASCADE)
