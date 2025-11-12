from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView
from .utils import create_balance
urlpatterns = [
    path('',views.index,name="index"),
    path('logout',LogoutView.as_view(template_name='myapp/logout.html'),name="logout"),
    path('login',views.login_user,name="login"),
    path('register',views.register,name="register"),
    # group function urls
    path('create_group',views.create_group,name="create_group"),
    path('group_index/<int:id>',views.group_index,name="group_index"),
    path('group_edit/<int:id>',views.edit_group,name="group_edit"),
    path('remove_member_group/<int:gid>/<int:uid>',views.remove_member_group,name="remove_member_group"),
    path('add_member_group/<int:gid>/<int:uid>',views.add_member_group,name="add_member_group"),
    # expense functions urls
    path('add_expense/<int:gid>',views.add_expense,name="add_expense"),
    path('delete_expense/<int:expid>',views.delete_expense,name="delete_expense"),
    path('view_expense/<int:expid>',views.view_expense,name="view_expense"),
    path('edit_expense/<int:expid>',views.edit_expense,name="edit_expense"),
    # settlement funtions url
    path('pay_amount/<int:gid>',views.pay_amount,name="pay_amount"),
    # Extra urls
    path('create_balance',create_balance,name="create_balance"),
]
