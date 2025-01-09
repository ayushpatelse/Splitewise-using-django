from django.contrib import messages
import datetime
from django.http import JsonResponse
from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth import login,authenticate
from django.contrib.auth.decorators import login_required
from .models import Group,Person,Expense,ExpenseShare,Balance,Settlement,SettleTran
from .forms import RegisterUser,CreateGroup,AddExpense,SettlementForm
from django.db.models import Sum
from .utils import remain_balance,create_expense_shares
# Create your views here.
@login_required
def index(request):
    
    person = Person.objects.get(user__id=request.user.id)
    #print("person",person.id)
    groups = Group.objects.all().filter(members=person)
    balance = Balance.objects.filter(person=person).aggregate(total=Sum('amount'))['total'] or 0.0
    return render(request,"myapp/index.html",{"groups":groups,"balance":balance,'groupBals':None})

def register(request):
    if request.method == "POST":
        user_form = RegisterUser(request.POST)
        if user_form.is_valid() :
            user = user_form.save()
            return redirect('login') 
    else :
        user_form = RegisterUser()
    return render(request,"myapp/register.html",{'user':user_form})


# Never make function name and imported login have same name
def login_user(request):
    if request.method=="POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            print("Error Occured")

    return render(request,"myapp/login.html")

@login_required
def create_group(request):
    users = Person.objects.all()
    
    if request.method=="POST":
        group_name = request.POST['group_name']
        member_list = request.POST.getlist('members')
        try :
            group = Group.objects.create(
                groupName=group_name,
                made_by=Person.objects.get(user=request.user),
            )
            
            for member in member_list:
                if member != request.user:
                    group.members.add(Person.objects.get(user__username=member))
            
            group.members.add(Person.objects.get(user=request.user))
            print("Group created")
            return redirect('index')
        except :
            messages.warning(request,'Group name already exists.')
        
    
    return render(request,"myapp/create_group.html",{"persons":users})

@login_required
def group_index(request,id):
    current_user = Person.objects.get(user=request.user)
    group = Group.objects.get(id=id)
    expense_list = Expense.objects.filter(group=group).order_by('-date')
    members = group.members.get_queryset()
    expShareList = ExpenseShare.objects.filter(expense__group=group)
    settlements = Settlement.objects.filter(group=group)

    # Logic for each member amount 
    balance_dic = {}
    balances = Balance.objects.filter(group=group)
    for member in members:
        total_amount = balances.filter(person=member).aggregate(total=Sum('amount'))['total']
        balance_dic[member.name] = total_amount
    indivBal = balances.filter(person=current_user)
    context = {"balances":balance_dic,"User_bals":indivBal,"group":group,"members":members,'exp_lists':expense_list,'expShares':expShareList,"person":current_user}
    return render(request,"myapp/group_index.html",context=context)

@login_required
def edit_group(request,id):
    persons = Person.objects.all()
    group = Group.objects.get(id=id)
    members = group.members.get_queryset()
    return render(request,"myapp/edit_group.html",{"group":group,"members":members,"persons":persons})

@login_required
def remove_member_group(request,gid,uid):
    group = Group.objects.get(id=gid)
    person = Person.objects.get(user__id=uid)
    if person :
        if remain_balance(person.id,gid)==False:
            name = person.name.capitalize()
            messages.success(request , f'{name} has been removed')
            group.members.remove(
                person
            )
            
        else:
            name = person.name.capitalize()
            messages.warning(request,f"Please settle remaining balance of {name}"   )
            print('Please settle remaining balance')
    
    return redirect('group_edit',gid)    

@login_required
def add_member_group(request,gid,uid):
    group = Group.objects.get(id=gid)
    person = Person.objects.get(user__id=uid)
    if person  :
        group.members.add(
            person
        )
    return redirect('group_edit',gid)    

@login_required
def add_expense(request,gid):
    c_group = Group.objects.get(id=gid)  # Get the Group object
    # Access the members of the group
    lists_member = c_group.members.all()
    
    if request.method == "POST":
        expense_form = AddExpense(request.POST)
        
        if expense_form.is_valid():
            expense = expense_form.save()
            members = request.POST.getlist('members-included') or None
            amounts = request.POST.getlist('members-amount') 
            splitType =  request.POST.get('divide-amount-select')
            
            if len(amounts)>0 and splitType=='unequal':
                # print('list amount',"members",members,"amounts",amounts,"splitType",splitType)
                create_expense_shares(expense,splitType,members,amounts)
            elif splitType=='percent':
                percent = amounts
                create_expense_shares(expense,splitType,members,expense.amount,percent)        
            else:
                amounts = expense.amount
                # print("members",members,"amounts",amounts,"splitType",splitType)
                create_expense_shares(expense,splitType,members,expense.amount)
            print(members,amounts)
            return redirect('group_index',gid)
    else:
        expense_form = AddExpense()

    return render(request,'myapp/add_expense.html',{"form":expense_form,"lists_member":lists_member,"user_group":c_group})

@login_required
def view_expense(request,expid):
    expense =Expense.objects.get(id=expid)
    expenseShare = ExpenseShare.objects.filter(expense=expense)

    return render(request,'myapp/view_expense.html',{'expense':expense,'shares':expenseShare})

@login_required
def delete_expense(request,expid):
    expense = get_object_or_404(Expense,id=expid)
    gid = expense.group.id
    expense.delete()
    return redirect('group_index',id=gid) 

@login_required
def edit_expense(request,expid):
    expense = get_object_or_404(Expense,id=expid)
    shares = ExpenseShare.objects.filter(expense=expense)
    c_group = Group.objects.get(id=expense.group.id)  # Get the Group object
    # Access the members of the group
    lists_member = c_group.members.all()
    m_ids_shares = [share.expsPerson.id for share in shares] 
    # print(m_ids_shares)
    if request.method == "POST":
        expense_form = AddExpense(request.POST,instance=expense)
    
        if expense_form.is_valid():
            expense = expense_form.save()
            members = request.POST.getlist('members-included') or None
            amounts = request.POST.getlist('members-included-amount') 
            splitType =  request.POST.get('divide-amount-select')
            # check the remaining value
            print('Before forloop',[ str(members[i] + ':' + amounts[i]) for i in range(len(members)) ])
            for id in m_ids_shares:
                if str(id) in members:
                    m_share = shares.get(expsPerson__id=id)
                    index = members.index(str(id))
                                           
                    if  len(amounts)>0:
                        if m_share.expsAmount != int(amounts[index]):
                            m_share = int(amounts[index])
                            # m_share.save()
                        amounts.pop(index)
                    members.pop(index)
                else: 
                    m_share = shares.get(expsPerson__id=id)
                    print(m_share,False)
            print('After forloop',[ str(members[i] + ':' + amounts[i]) for i in range(len(members)) ])
            

            # if len(amounts)>0 and splitType=='unequal':
            #     print('list amount',"members",members,"amounts",amounts,"splitType",splitType)
            #     # create_expense_shares(expense,splitType,members,amounts)
            # elif splitType=='percent':
            #     print('percent amount',"members",members,"amounts",amounts,"splitType",splitType)
            #     percent = amounts
            #     # create_expense_shares(expense,splitType,members,expense.amount,percent)        
            # else:
            #     amounts = expense.amount
            #     print("members",members,"amounts",amounts,"splitType",splitType)
            #     # create_expense_shares(expense,splitType,members,expense.amount)
            #return redirect('group_index',c_group.id)
    else:
        expense_form = AddExpense(instance=expense)
    return render(request,'myapp/edit_expense.html',{'form':expense_form,'expense':expense,"lists_member":lists_member,'exp_members':m_ids_shares})

@login_required
def pay_amount(request,gid):
    group = Group.objects.get(id=gid) or None
    members = group.members.all()
    initial_data = {
        'amount': request.GET.get('value') or 0,
        'payer_id':int(request.GET.get('payer') )or None,
    }
    if request.method=="POST":
        data = request.POST
        pay_form = SettlementForm(data)
        if pay_form.is_valid():
            form = pay_form.save(commit=False)
            print("Form valid")

            form.group=group
            form.save() 
            messages.success(request,f'{form.payer} has paid {form.amount} to {form.payee}')
            return redirect('group_index',gid)   

        else:
            print("Form not valid")
    else: 
        pay_form = SettlementForm()    

    return render(request,'myapp/pay_amount.html',{'form':pay_form,'group':group,'members':members,'data':initial_data})


