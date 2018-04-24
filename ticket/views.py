from django.shortcuts import render

from django.contrib.auth import views
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
# Create your views here.
from ticket.forms import TicketForm


@login_required
def dashboard(request):
    return render(request, 'ticket\dashboard.html', locals())

#用户登陆选项，所有的函数将会返回一个template_response的实例，用来描绘页面，同时你也可以在return之前增加一些特定的功能
#用户登陆
def login(request):
    #extra_context是一个字典，它将作为context传递给template，这里告诉template成功后跳转的页面将是/index
    template_response = views.login(request, extra_context={'next': '/t/dashboard/'})
    return template_response

#用户退出
def logout(request):
    #logout_then_login表示退出即跳转至登陆页面，login_url为登陆页面的url地址
    template_response = views.logout_then_login(request,login_url='/t/login/')
    return template_response

#密码更改
@login_required
def password_change(request):
    #post_change_redirect表示密码成功修改后将跳转的页面.
    template_response = views.password_change(request,post_change_redirect='/index/')
    return template_response

#增加
def ticket_add(request):
    #从TaskForm获取相关信息
    form = TicketForm(request.POST or None)
    if form.is_valid():
        pass

    context = {
        'form': form,
        'page_title': '任务处理',
        'sub_title': '新建任务',
    }
    return render(request, 'ticket/ticket_add.html',  context)