from django.contrib import admin
from .models import Person,Group,Expense,ExpenseShare,Settlement,Balance,SettleTran
# Register your models here.
admin.site.register(Person)
admin.site.register(Group)
admin.site.register(Expense)
admin.site.register(ExpenseShare)
admin.site.register(Settlement)
admin.site.register(Balance)
admin.site.register(SettleTran)