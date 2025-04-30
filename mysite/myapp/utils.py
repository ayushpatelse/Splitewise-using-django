# Implement the function to use in the program
from .models import Person,Group,Expense,ExpenseShare,Balance
from django.http.response import JsonResponse
from django.db.models import Sum
from django.db.models import Q

def create_balance(request):
    persons = Person.objects.all()
    groups = Group.objects.all()
    expenses = Expense.objects.all()
    shareList = ExpenseShare.objects.all()

    for person in persons:
        print("balance created of",person.name)
        g_member = groups.filter(members=person)
        for group in g_member:
            total_owed = shareList.filter(expsPerson=person).filter(expense__group=group).aggregate(total_owed=Sum('expsAmount'))['total_owed'] or 0.0
            total_gets = expenses.filter(payer=person,group=group).aggregate(total_gets=Sum('amount'))['total_gets'] or 0.0
            balance = total_owed - total_gets
            shares = shareList.filter(expsPerson=person).filter(expense__group=group)
            if (Balance.objects.filter(person=person,group=group).exists())==False:
                instance =  Balance.objects.create(
                            person=person,
                            amount=balance,
                            group=group,
                        )
            
            else:
                print("Share id present:")
            #print("total_gets:",total_gets,'total_owed:',total_owed,'balance:' ,total_owed - total_gets,'group:',group,'/n')
        print('/n/n')


    return JsonResponse('Balance table populated',safe=False)

# Returns Boolean True if has balance else False 
def remain_balance(personId,groupId):

    flag = 0
    total_amount = Balance.objects.filter(person__id=personId,group__id=groupId).aggregate(total_amt=Sum('amount'))['total_amt'] or 0 
    
    if int(total_amount) != int(0.0):
        flag = 1
    print(total_amount)
    return bool(flag)

def create_expense_shares(expense:Expense,split_type:str,members,amounts=None,percantage=None):
    try:
        if len(members)>0 and isinstance(members[0],Person):
            list_members = members
        elif len(members)>0 and type(members[0])==str:
            list_members = [Person.objects.get(id=int(m_id)) for m_id in members  ]
        else:
            ValueError('Members error')
        
        
        match split_type:
            case 'equal':
                share_amt = expense.amount / len(list_members)
                for member in list_members:
                    m_object = ExpenseShare.objects.create(
                        expsAmount=float(share_amt),
                        expsPerson=member,
                        expense=expense,
                        splitType=split_type,
                    )

            case 'unequal':
                if '' in amounts: # remove blank space
                    amounts = [amount for amount in amounts if amount!='' ]

                if len(list_members)==len(amounts):
                    for i,member in enumerate(list_members):
                        ExpenseShare.objects.create(
                        expsAmount=float(amounts[i]),
                        expsPerson=member,
                        expense=expense,
                        splitType=split_type,
                        ) 
                else:
                    raise ValueError("Problem in unequal Expense Share")

            case 'percent':
                if '' in percantage: # remove blank space
                    percantage = [percent for percent in percantage if percent!='' ]

                for i,member in enumerate(list_members):
                    share_amt = float((expense.amount * int(percantage[i]))/100)
                    ExpenseShare.objects.create(
                        expsAmount=share_amt,
                        expsPerson=member,
                        expense=expense,
                        splitType=split_type,
                    )
            case _ :
                raise ValueError("Invalid Expense Share")
    except Exception as error:
        print("Expense Share not created")
        print(error)
    
    
# Expense Payer Changed
def expense_payer_change(expense_id,new_payer_id):
    try:
        if(expense_id==new_payer_id):
            raise Exception((str(expense_id) + ' === ' + str(new_payer_id)))
        
        expense = Expense.objects.get(id=expense_id)
        new_payer = Person.objects.get(id=new_payer_id)
        old_payer = expense.payer 
        group = expense.group
        
        balances = Balance.objects.filter(group=group)
        shares = ExpenseShare.objects.filter(expense=expense)
        expShareOld = shares.filter(expsPerson=old_payer).first().expsAmount
        print("expShareOld "+ str(expShareOld))
        
        # reduce the balance
        newBalance = balances.filter(person=new_payer,rPerson=old_payer).first()
        oldBalance = balances.filter(person=old_payer,rPerson=new_payer).first()
        if(newBalance.person==new_payer and newBalance.rPerson==old_payer ):
            newBalance.amount -= (expense.amount )
        
        # add the balance
        if(oldBalance.person==old_payer and oldBalance.rPerson==new_payer ):
            oldBalance.amount += (expense.amount )
        print(str(old_payer) + "  " + str(new_payer))
        # save the balance expesne
        try:

            newBalance.save()
            oldBalance.save()
            print("balance saved")
        except:
            raise Exception("Error! - Problem saving newBalance or oldBalance line 131 utils.py")

        if new_payer in group.members.all():
            payer_amt = shares.get(expsPerson=new_payer)
            # balances(person=old_payer)
        else:
            print(new_payer.name + " Not in Group :" + group.groupName)
        # print(expense,new_payer)
    except Exception as error :
        print('Error - function: expense_payer_change ,' ,error)
        