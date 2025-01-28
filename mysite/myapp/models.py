from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

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
    amount = models.FloatField(default=0.0)
    description = models.TextField(default=None,blank=True)
    payer = models.ForeignKey(Person,on_delete=models.CASCADE)
    group = models.ForeignKey(Group,on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now=True)
    image = models.ImageField(default='static/images/uses/default-1.png')

    def __str__(self):
        return self.expenseName
    
class ExpenseShare(models.Model):
    SPLIT_TYPE = {
        (1,'equal'),
        (2,'unequal'),
        (3,'percent'),
    }
    expsAmount = models.FloatField()
    expsPerson = models.ForeignKey(Person,on_delete=models.CASCADE)
    expense = models.ForeignKey(Expense,on_delete=models.CASCADE)
    splitType = models.CharField(max_length=50,default='equal')

    def __str__(self):
        return  self.expsPerson.name + ' shares ' + str(self.expsAmount) +  ' in ' + self.expense.expenseName +"Of " + self.expense.group.groupName

class Settlement(models.Model):
    payer = models.ForeignKey(Person,on_delete=models.CASCADE,related_name='amount_payer')
    payee = models.ForeignKey(Person,on_delete=models.CASCADE,related_name='amount_receiver')
    date = models.DateTimeField(auto_now=True)
    amount = models.FloatField(default=0.0)
    group = models.ForeignKey(Group,on_delete=models.CASCADE)

    def __str__(self):
        return str(self.payer) + ' paid '+ str(self.payee) + ' on ' + str(self.date.date())

    def clean(self):
        if self.payee.id == self.payer.id:
            raise ValidationError('Payer and Payee should not be same')
        elif (self.amount==0.0):
            raise ValidationError('Amount could not be 0.0')

    def save(self,*args,**kwargs):
        self.clean()
        return super().save()
    
class Balance(models.Model):
    person = models.ForeignKey(Person,on_delete=models.CASCADE,related_name="owing_person")
    amount = models.FloatField(default=0.0)
    updated_on = models.DateTimeField(auto_now=True)
    group = models.ForeignKey(Group,on_delete=models.CASCADE)
    rPerson  = models.ForeignKey(Person,on_delete=models.CASCADE,related_name="receive_person",default=2)
    def __str__(self):
        return str(self.person) + ' has balance ' + str(self.amount) +' with ' + self.rPerson.name + ' in ' + self.group.groupName


class SettleTran(models.Model):
    balance = models.ForeignKey(Balance,on_delete=models.CASCADE)
    settlement = models.ForeignKey(Settlement,on_delete=models.CASCADE)
