# Splitewise-using-django


-------------------------------------------Models---------------------------------------------------------------------

Person

Name: string (Default: -)
User: OneToOneField ( with user models, CASCADE on Delete)
image: Image (Default)

Groups

groupName: string (Default: -)
made_by: Relationship (Two-way Relationship with Users; Many to one, Attribute Key (related collection): groups, Cascade on delete)
members: Relationship (Two-way Relationship with Users; Many to Many, Attribute Key (related collection): UserMember, Set Null on delete)

Expense 

amount: FloatField (default=0.0)
description: TextField ()
payer: ForeignKey with Person, on_delete=models.CASCADE
group: ForeignKey with Group, on_delete=models.CASCADE
date: DateTimeField ( set auto now true)
image: ImageField ( default )


ExpenseShare

expsAmount: FloatField
expsPerson: ForeignKey with person
expense: ForeignKey with Expense

Settlement

payer: ForeignKey with Person,on_delete = model.CASCADE
payee: ForeignKey with Person,on_delete = model.CASCADE
amount: FloatField field  
date: DateTimeField (auto_created=now)
group: ForeignKey with Group,on_delete = model.CASCADE

Balances

person: ForeignKey with Person
amount: FloatField field (amount owed : postive(+), amount gets back: negative(-)) 
group: ForeignKey field with group
updated_date: DateTimeField ()
rPerson: receiver person

SettleTrans

balance: ForeignKey with balance
settlement: ForeignKey with settlement
---------------------------------------------Signals--------------------------------------------------

Function: create_person (Using User model for auth)
- Creates person when new User register

Function: create_initial_balance_group
- creates balance with each member

Function: create_expense_share_balance 
- Populates shares of each member of group in expense share ,when new expense is added
- Adjust the balance according to the new balance

Function: delete_expense_adjust_balance
- 
Function: adjust_balance
- changes balance when new settlement is created  
