import json
from django.contrib import messages
from django.core.serializers import serialize
from datetime import datetime
from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth import login,authenticate
from django.contrib.auth.decorators import login_required
from .models import Group,Person,Expense,ExpenseShare,Balance,Settlement,SettleTran
from .forms import RegisterUser,CreateGroup,AddExpense,SettlementForm
from django.db.models import Sum
from .utils import remain_balance,create_expense_shares,expense_payer_change
from django.db.models import Q

# 404 Redirect
def custom_page_404(request,exception=None):
    print("Entered")
    redirect('/')

# Create your views here.
@login_required
def index(request):
    
    person = Person.objects.get(user__id=request.user.id)
    #print("person",person.id)
    groups = Group.objects.all().filter(members=person)
    balances = Balance.objects.filter(person=person)
    balance = balances.aggregate(total=Sum('amount'))['total'] or 0.0
    balanceList = {}
    for group in groups:
        # print(balances.filter(group=group).aggregate(total=Sum('amount'))or 0.0)
        balanceList[group.groupName.capitalize()] = balances.filter(group=group).aggregate(total=Sum('amount'))['total'] or 0.0
    # print(balanceList)
    return render(request,"myapp/index.html",{"groups":groups,"balance":balance,'groupBals':balanceList})

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
    months= {1: 'January', 2: 'February', 3: 'March', 4: 'April', 5: 'May', 6: 'June', 7: 'July', 8: 'August', 9: 'September', 10: 'October', 11: 'November', 12: 'December'}
    query ={}
    current_user = Person.objects.get(user=request.user)
    group = Group.objects.get(id=id)
    expense_list:Expense = Expense.objects.filter(group=group).order_by('-date')
    expense_by_month = {}

    # Filter Logic
    if request.GET.get("keyword"):
        query["keyword"] = request.GET.get("keyword")
        expense_list = expense_list.filter(Q(expenseName__icontains=query['keyword'])|Q(description__icontains=query['keyword']))
    
    
    if request.GET.get("d_from"):
        try:
            query["d_from"] = request.GET.get("d_from")
            date_from = datetime.strptime(query['d_from'],'%d/%m/%Y')
            expense_list = expense_list.filter(date__gte=date_from)
        except Exception as e:
            print(e)

    if request.GET.get("d_to"):
        try:
            query["d_to"] = request.GET.get("d_from")
            date_to = datetime.strptime(query['d_to'],'%d/%m/%Y')
            expense_list = expense_list.filter(date__gte=date_to)
        except Exception as e:
            print(e)
    
    if request.GET.get("p_from"):
        query["p_from"] = request.GET.get("p_from")
        expense_list = expense_list.filter(amount__gte=query['p_from'])
    
    if request.GET.get("p_to"):
        query["p_to"] = request.GET.get("p_to")
        expense_list = expense_list.filter(amount__lte=query['p_to'])
    

    

    for exp in expense_list:
        month = months[exp.date.month]
        year = str(exp.date.year)
        key = month+ ' ' + year
        if key not in expense_by_month.keys():
            expense_by_month[key] = [exp]
        else:
            expense_by_month[key].append(exp)
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

    context = {"balances":balance_dic,"User_bals":indivBal,"group":group,"members":members,'expShares':expShareList,"person":current_user,'expByMonth':expense_by_month,"query":query}
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
    person = Person.objects.get(id=uid)
    print(group,uid)
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
            amounts = request.POST.getlist('members-included-amount') 
            splitType =  request.POST.get('divide-amount-select')
            
            if len(amounts)>0 and splitType=='unequal':
                create_expense_shares(expense,splitType,members,amounts)
            elif splitType=='percent':
                percent = amounts
                create_expense_shares(expense,splitType,members,expense.amount,percent)        
            else:
                create_expense_shares(expense,splitType,members,expense.amount)        

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
    expense_obj = get_object_or_404(Expense,id=expid)
    shares = ExpenseShare.objects.filter(expense=expense_obj)
    expense_payer_id = expense_obj.payer.id
    c_group = Group.objects.get(id=expense_obj.group.id)  # Get the Group object
    # Access the members of the group
    lists_member = c_group.members.all()
    shareIds = [share.expsPerson.id for share in shares]
    json_share = serialize('json',shares)
    
    
    if request.method == "POST":
        expense_form = AddExpense(request.POST,instance=expense_obj)
        payer_changed = int(request.POST.get('payer')) != expense_payer_id   
        if expense_form.is_valid():
            if payer_changed:
                print('payer change')
                expense_id = request.POST.get('expense-id')
                new_payer  = request.POST.get('payer')
                expense_payer_change(expense_id=expense_id,new_payer_id=new_payer)
            else:
                print('Not Changed')
            expense = expense_form.save()
            members = request.POST.getlist('members-included') or []
            amounts = request.POST.getlist('members-included-amount') or []
            splitType =  request.POST.get('divide-amount-select') or 'equal'
            
            if '' in amounts:
                amounts = [amount for amount in amounts if amount!='' ]
            shares.delete()
            
            # same logic as 
            if len(amounts)>0 and splitType=='unequal':
                # print('list amount',"members",members,"amounts",amounts,"splitType",splitType)
                create_expense_shares(expense,splitType,members,amounts)
            elif splitType=='percent':
                # print('percent amount',"members",members,"amounts",amounts,"splitType",splitType)
                percent = amounts
                create_expense_shares(expense,splitType,members,expense.amount,percent)        
            else:
                amounts = expense.amount
                # print("members",members,"amounts",amounts,"splitType",splitType)
                create_expense_shares(expense,splitType,members,expense.amount)
            try:
                shareIds = [int(id) for id in members]
            except Exception as error:
                print(error)
            
            return redirect('group_index',expense_obj.group.id)

    else:
        expense_form = AddExpense(instance=expense_obj)
    return render(request,'myapp/edit_expense.html',{'form':expense_form,'expense':expense_obj,"lists_member":lists_member,'exp_members':shareIds,'jShares':json_share})

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

            form.group=group
            form.save() 
            messages.success(request,f'{form.payer} has paid {form.amount} to {form.payee}')
            return redirect('group_index',gid)   

        else:
            print("Form not valid")
    else: 
        pay_form = SettlementForm()    

    return render(request,'myapp/pay_amount.html',{'form':pay_form,'group':group,'members':members,'data':initial_data})


