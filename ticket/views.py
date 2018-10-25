import datetime

from django.db.models import Sum, Count, Q

from django.contrib.auth import views
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from ticket import utils
from ticket.models import Ticket, SuperLoan, Loan_Order, DashBoard
from django.contrib.auth.models import User
from ticket.forms import UserCreatForm, UserManageForm, UserChangePasswordForm


@login_required
def dashboard(request):
    ts = Ticket.objects.values('t_status', 't_type').annotate(t_count=Count('id'), sum_money=Sum('piaomianjiage'))
    kudianc = 0
    kudians = 0
    kuzhic = 0
    kuzhis = 0
    chidianc = 0
    chidians = 0
    chizhic = 0
    chizhis = 0
    for t in ts:
        if t['t_status'] == 1:
            if t['t_type'] == 1:
                kuzhic = t['t_count']
                kuzhis = round(t['sum_money'], 2)
                pass
            elif t['t_type'] == 2:
                kudianc = t['t_count']
                kudians = round(t['sum_money'], 2)
                pass
        elif t['t_status'] == 5:
            if t['t_type'] == 1:
                chizhic = t['t_count']
                chizhis = round(t['sum_money'], 2)
                pass
            elif t['t_type'] == 2:
                chidianc = t['t_count']
                chidians = round(t['sum_money'], 2)
                pass
        pass
    kuc = kudianc + kuzhic
    kus = round(kudians + kuzhis, 2)
    chic = chidianc + chizhic
    chis = round(chidians + chizhis, 2)
    allc = kuc + chic
    alls = round(kus + chis, 2)

    today = datetime.datetime.now().strftime("%Y-%m-%d")
    threeday = (datetime.datetime.now() + datetime.timedelta(days=3)).strftime("%Y-%m-%d")
    # count_t = Ticket.objects.filter(Q(t_status=5)&Q(daoqiriqi__gt=today)).count()
    ts = Ticket.objects.filter(Q(t_status=5) & Q(daoqiriqi__lte=today)).values('t_status').annotate(t_count=Count('id'),
                                                                                                    sum_money=Sum(
                                                                                                        'piaomianjiage'))
    daoqizaichi_count = 0
    daoqizaichi_sum = 0
    for t in ts:
        if t['t_status'] == 5:
            daoqizaichi_count = t['t_count']
            daoqizaichi_sum = round(t['sum_money'], 2)
    ts = Ticket.objects.filter(Q(t_status=1) & Q(daoqiriqi__lte=threeday)).values('t_status').annotate(
        t_count=Count('id'), sum_money=Sum('piaomianjiage'))
    daoqikucun_count = 0
    daoqikucun_sum = 0
    for t in ts:
        if t['t_status'] == 1:
            daoqikucun_count = t['t_count']
            daoqikucun_sum = round(t['sum_money'], 2)
    # ts = SuperLoan.objects.filter(Q(needpay_sum__gt=0)|Q(needpay_lixi__gt=0)).annotate(t_count = Count('id'),sum_money=Sum('needpay_sum'),sum_lixi=Sum('needpay_lixi'))

    superLoans = SuperLoan.objects.filter(is_payed=False, lixi_end_date__lte=threeday)
    loan_count = 0
    loan_sum = 0
    for superLoan in superLoans:
        loan_count += 1
        loan_sum = loan_sum + superLoan.benjin_needpay + superLoan.lixi_needpay
    # payfee_data = Fee.objects.filter(Q(order=pk)&(Q(fee_type=3)|Q(fee_type=5)|Q(fee_type=7))).order_by('-pub_date')

    loanOrders = Loan_Order.objects.filter(is_payed=False)
    daishou_count = 0
    daishou_sum = 0
    daifu_count = 0
    daifu_sum = 0
    for loanOrder in loanOrders:
        if loanOrder.order_type == 4:
            daifu_count += 1
            daifu_sum += loanOrder.benjin_needpay + loanOrder.lixi_needpay
        if loanOrder.order_type == 3:
            daishou_count += 1
            daishou_sum += loanOrder.benjin_needpay + loanOrder.lixi_needpay

    dashs = DashBoard.objects.filter().order_by('-day')
    dashs, page_range, count, page_nums = utils.pagination(request, dashs)

    return render(request, 'ticket/dashboard.html', locals())


# 用户登陆
def login(request):
    template_response = views.login(request, extra_context={'next': '/t/dashboard/'})
    return template_response


# 用户退出
def logout(request):
    # logout_then_login表示退出即跳转至登陆页面，login_url为登陆页面的url地址
    template_response = views.logout_then_login(request, login_url='/t/login/')
    return template_response


@login_required
def user_list(request):
    form = UserCreatForm(request.POST or None)
    oper_form = UserManageForm(request.POST or None)
    context = {}
    if request.method == 'POST':
        if form.is_valid():
            oper_form = UserManageForm()
            loginname = form.cleaned_data.get('loginname')
            try:
                user = User.objects.create_user(loginname, None, 'abcd1111')
                user.last_name = form.cleaned_data.get('username')
                user.save()
                context['message'] = u'保存成功'
            except:
                context['errormsg'] = u'该用户已存在'
        elif oper_form.is_valid():
            form = UserCreatForm()
            operation = oper_form.cleaned_data.get('operation')
            ids = request.POST['ids']
            if len(ids) > 0:
                if operation == '1':
                    users = User.objects.filter(id__in=ids.split(','))
                    for u in users:
                        u.set_password('abcd1111')
                        u.save()
                    context['message'] = u'重置成功，密码为abcd1111'
                elif operation == '2':
                    User.objects.filter(id__in=ids.split(',')).update(is_active=True)
                    context['message'] = u'启用成功'
                    pass
                elif operation == '3':
                    User.objects.filter(id__in=ids.split(',')).update(is_active=False)
                    context['message'] = u'停用成功'
                    pass
            else:
                context['errormsg'] = u'请选择至少一个账号'

    context['form'] = form
    context['oper_form'] = oper_form
    raw_data = User.objects.filter(is_superuser=False)
    list_template = 'ticket/user_list.html'
    return utils.get_paged_page(request, raw_data, list_template, context)


# 密码更改
@login_required
def change_password(request):
    form = UserChangePasswordForm(request.POST or None)
    context = {
        'form': form,
    }
    if request.method == 'POST':
        if form.is_valid():
            u = request.user
            if u.check_password(form.cleaned_data.get('old_password')):
                password1 = form.cleaned_data.get('new_password')
                password2 = form.cleaned_data.get('new_password_2')
                if password1 and password2 and len(password1)>0 and password1 == password2:
                    u.set_password(password1)
                    u.save()
                    context['message'] = u'修改成功'
                else:
                    context['errormsg'] = u'新密码不一致或错误'

            else:
                context['errormsg'] = u'旧密码错误'

    return render(request, 'ticket/user_change_password.html', context)
