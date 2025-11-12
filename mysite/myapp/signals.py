from django.db.models.signals import post_save,m2m_changed,pre_delete
from django.dispatch import receiver
from .models import Person,User,Expense,ExpenseShare,Group,Settlement,Balance,SettleTran  # Replace with your model
from django.db.models import Q

@receiver(post_save,sender=User)
def create_person(sender,instance,created,**kwargs):
    if created:
        Person.objects.create(
            user=instance,
            name= instance.username,
        )
        print("Profile created")
    else:
        print("Profile not created")

@receiver(m2m_changed,sender=Group.members.through)
def create_balance_group(sender,instance,action,**kwargs):
    group = instance
    if action=='post_add':
        print("Create Balance: signal",action)
        members = group.members.all()
        for member in members:
            for rMember in members:
                if member.id != rMember.id:
                    Balance.objects.get_or_create(
                        person=member,
                        rPerson=rMember,
                        amount=0,
                        group=group
                    ) 
    else:
        print("Create Balance:signal",action)


@receiver(post_save,sender=ExpenseShare)
def adjust_balance_expenseshare(sender,instance,created,**kwargs):
    if created:
        share = instance
        payer = share.expense.payer
        group = share.expense.group
        balances = Balance.objects.filter(group=group).filter(Q(person=share.expsPerson,rPerson=payer)| Q(person=payer,rPerson=share.expsPerson))
       
        # Reduce the balance , where person = Expense Payer
        addBalance = balances.filter(person=payer,rPerson=share.expsPerson)
       
        # print('redBalance :',redBalance)
        amt = share.expsAmount
        if addBalance.count() > 0:
            temp = addBalance.first()
            temp.amount = temp.amount - amt
            temp.save()
            #print("reduce Amount:",temp.amount ,'AmtShare',amt, 'final:',temp.amount -  amt)
            
        # Add the balance , where rPerson = Expense Payer
        redBalance = balances.filter(person=share.expsPerson,rPerson=payer)
        # print('addBalance :',redBalance)
        if redBalance.count() > 0:
            temp = redBalance.first()
            temp.amount = temp.amount +  amt
            temp.save()
           # print("add Amount:",temp.amount ,'AmtShare',amt, 'final:',temp.amount +   amt)
            
    else:
        print("Expense error ,created:",created)

@receiver(pre_delete,sender=Expense)
def delete_expense_adjust_balance(sender,instance,**kwargs):
    expense = instance
    expShare = ExpenseShare.objects.filter(expense=expense)
    balances = Balance.objects.filter(group=expense.group)
    # Reduce balance 
    payer = expense.payer
    for share in expShare:
        person = share.expsPerson
        l_balances = balances.filter(person=person)
        print(l_balances)
        for bal in l_balances:
            temp = bal
            if (bal.person.name == payer.name):
                print('    ',bal.person.name,' has ',bal.amount,' with ',bal.rPerson.name,'add balance')
                temp.amount += share.expsAmount
                temp.save()

            if (bal.rPerson.name == payer.name): 
                print('    ',bal.person.name,' has ',bal.amount,' with ',bal.rPerson.name,'reduce balance')
                temp.amount -= share.expsAmount
                temp.save()



@receiver(post_save,sender=Settlement)
def adjust_balance(sender,instance,created,**kwargs):
    if created:
        settlement = instance
        balances = Balance.objects.filter(group=settlement.group).filter(Q(person=settlement.payer,rPerson=settlement.payee) | Q(person=settlement.payee,rPerson=settlement.payer) )
        print(balances.count())
        for balance in balances:
            if (balance.person.id == settlement.payer.id ):
                balance.amount -= settlement.amount
                balance.save()
            if (balance.rPerson.id == settlement.payer.id ):
                balance.amount += settlement.amount
                balance.save()
        print('Balance changed after settlement')
    else:
        print("Settlement not created")
