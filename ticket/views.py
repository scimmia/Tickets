import csv
import os
import uuid

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Sum, Count
from django.shortcuts import render, redirect, get_object_or_404

from django.contrib.auth import views
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
# Create your views here.
from django.urls import reverse

from ticket.forms import TicketForm, CardForm, TicketEditForm, PoolForm, TicketFeeForm
from ticket.models import Card, Fee, Ticket, StoreFee, PoolFee, Pool, InpoolPercent, TicketsImport


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

def ticket_instore(ticket_pk):
    ticket = Ticket.objects.get(pk=ticket_pk)
    storefee = StoreFee()
    storefee.ticket = ticket
    storefee.money = ticket.piaomianjiage
    storefee.storefee_status = 1
    storefee.save()
    pass
def ticket_outstore(ticket_pk):
    ticket = Ticket.objects.get(pk=ticket_pk)
    storefee = StoreFee()
    storefee.ticket = ticket
    storefee.money = 0- ticket.piaomianjiage
    storefee.storefee_status = 2
    storefee.save()
    pass
def ticket_inpool(ticket_pk):
    ticket = Ticket.objects.get(pk=ticket_pk)
    item = InpoolPercent.objects.last()
    if not item:
        item = InpoolPercent()
        item.inpoolPer = 100
        item.save()
    p = Pool.objects.last()
    if not p:
        p = Pool()
    pool = Pool()
    pool.totalmoney = p.totalmoney + ticket.piaomianjiage * item.inpoolPer /100
    pool.promoney = p.promoney
    pool.unusemoney = p.unusemoney + ticket.piaomianjiage * item.inpoolPer /100
    pool.usedmoney = p.usedmoney
    pool.ticket = ticket
    pool.money = ticket.piaomianjiage
    pool.pool_status = 1
    pool.save()
    pass

def ticket_outpool(ticket_pk):
    ticket = Ticket.objects.get(pk=ticket_pk)
    item = InpoolPercent.objects.last()
    if not item:
        item = InpoolPercent()
        item.inpoolPer = 100
        item.save()
    p = Pool.objects.last()
    if not p:
        p = Pool()
    pool = Pool()
    pool.totalmoney = p.totalmoney - ticket.piaomianjiage * item.inpoolPer /100
    pool.promoney = p.promoney
    pool.unusemoney = p.unusemoney - ticket.piaomianjiage * item.inpoolPer /100
    pool.usedmoney = p.usedmoney
    pool.ticket = ticket
    pool.money = 0 - ticket.piaomianjiage
    pool.pool_status = 2
    pool.save()
    pass

def ticket_pay(ticket_pk):
    ticket = Ticket.objects.get(pk=ticket_pk)
    card = Card.objects.get(pk=ticket.gourucard.pk)
    fee_ins = Fee()
    fee_ins.ticket = ticket
    fee_ins.yinhangka = card
    fee_ins.money = 0 - ticket.gourujiage
    fee_ins.name = '购票付款'
    fee_ins.save()
    card.money = card.money + fee_ins.money
    card.save()

def ticket_poolpay(ticket_pk):
    ticket = Ticket.objects.get(pk=ticket_pk)
    p = Pool.objects.last()
    if not p:
        p = Pool()
    pool = Pool()
    pool.totalmoney = p.totalmoney
    pool.promoney = p.promoney
    pool.unusemoney = p.unusemoney - ticket.piaomianjiage
    pool.usedmoney = p.usedmoney + ticket.piaomianjiage
    pool.ticket = ticket
    pool.money = 0 - ticket.piaomianjiage
    pool.pool_status = 5
    pool.save()

def ticket_sold(ticket_pk):
    ticket = Ticket.objects.get(pk=ticket_pk)
    card = Card.objects.get(pk=ticket.maichucard.pk)
    fee_ins = Fee()
    fee_ins.ticket = ticket
    fee_ins.yinhangka = card
    fee_ins.money = ticket.gourujiage
    fee_ins.name = '卖票收款'
    fee_ins.save()
    card.money = card.money + fee_ins.money
    card.save()

def card_fee(card_pk,money,name):
    card = Card.objects.get(pk=card_pk)
    fee_ins = Fee()
    fee_ins.yinhangka = card
    fee_ins.money = money
    fee_ins.name = name
    fee_ins.save()
    card.money = card.money + fee_ins.money
    card.save()

#增加
def ticket_add(request):
    form = TicketForm(request.POST or None)
    form.fields['gourujiage'].disabled = True  # text input
    form.fields['maichujiage'].disabled = True  # text input
    form.fields['lirun'].disabled = True  # text input

    #从TaskForm获取相关信息
    if form.is_valid():
        if ((not form.cleaned_data.get('gouruzijinchi')) and (not form.cleaned_data.get('gourucard'))
                or (form.cleaned_data.get('gouruzijinchi') and form.cleaned_data.get('gourucard'))):
            message = u'请选择“资金池购入”或“购入卡”中的一项'
            return render(request, 'ticket/ticket_add.html',locals())
        elif (form.cleaned_data.get('t_status') == 3):
            if not form.cleaned_data.get('maichucard'):
                message = u'请选择“卖出卡”'
                return render(request, 'ticket/ticket_add.html', locals())
            elif not form.cleaned_data.get('maipiaoren'):
                message = u'请填写“买票人”'
                return render(request, 'ticket/ticket_add.html',locals())
        times = 1
        if form.cleaned_data.get('fenshu') and form.cleaned_data.get('fenshu')>1:
            times = form.cleaned_data.get('fenshu')
        instance = form.save(commit=False)
        instance.gourujiage = instance.piaomianjiage * (1 - instance.gouruhuilv)
        instance.maichujiage = instance.piaomianjiage * (1 - instance.maichulilv)
        counter = 1
        while counter <= times:
            counter += 1
            instance.pk = None
            instance.save()
            if instance.t_status == 1:
                ticket_instore(instance.pk)
            elif instance.t_status == 5:
                ticket_inpool(instance.pk)
            elif instance.t_status == 3:
                instance.lirun = instance.maichujiage - instance.gourujiage
                instance.save()
                pass

            if instance.gouruzijinchi:
                ticket_poolpay(instance.pk)
                instance.pay_status = 2
                instance.save()
                pass
            else:
                if instance.pay_status == 2:
                    ticket_pay(instance.pk)
                    pass

            if instance.sell_status == 4:
                ticket_sold(instance.pk)
        return render(request, 'ticket/ticket_add.html',locals())
        # return redirect('ticket_list')
    else:
        return render(request, 'ticket/ticket_add.html',locals())
#修改数据,函数中的pk代表数据的id
def ticket_edit(request,  pk):
    ticket_ins = get_object_or_404(Ticket, pk=pk)
    message = None

    #从TaskForm获取相关信息
    if request.method == 'POST':
        POST = request.POST.copy()
        if ticket_ins.t_status == 3:
            POST['t_status'] = ticket_ins.t_status
            POST['maichulilv'] = ticket_ins.maichulilv
            POST['maichujiage'] = ticket_ins.maichujiage
            POST['maichucard'] = ticket_ins.maichucard.pk
            POST['maipiaoren'] = ticket_ins.maipiaoren
            POST['lirun'] = ticket_ins.lirun
        POST['qianpaipiaohao'] = ticket_ins.qianpaipiaohao
        POST['piaohao'] = ticket_ins.piaohao
        POST['chupiaohang'] = ticket_ins.chupiaohang
        POST['chupiaoriqi'] = ticket_ins.chupiaoriqi
        POST['daoqiriqi'] = ticket_ins.daoqiriqi
        POST['piaomianjiage'] = ticket_ins.piaomianjiage
        POST['gongyingshang'] = ticket_ins.gongyingshang
        POST['gouruhuilv'] = ticket_ins.gouruhuilv
        POST['gourujiage'] = ticket_ins.gourujiage
        POST['gouruzijinchi'] = ticket_ins.gouruzijinchi
        if not ticket_ins.gouruzijinchi:
            POST['gourucard'] = ticket_ins.gourucard.pk
        POST['lirun'] = ticket_ins.lirun
        if ticket_ins.pay_status == 2:
            POST['pay_status'] = ticket_ins.pay_status
        if ticket_ins.sell_status == 4:
            POST['sell_status'] = ticket_ins.sell_status
        form = TicketEditForm(POST, instance=ticket_ins )
        if form.is_valid():
            if ('t_status' in form.changed_data) and (request.POST.get('t_status') == '3')\
                    and (not request.POST.get('maichucard')):
                    message = u'请选择“卖出卡”'
            elif ('t_status' in form.changed_data) and (request.POST.get('t_status') == '3')\
                    and (not request.POST.get('maipiaoren')):
                    message = u'请填写“买票人”'
            else:
                instance = form.save(commit=False)
                if 't_status' in form.changed_data:
                    old_s = Ticket.objects.get(pk=pk).t_status
                    new_s = form.cleaned_data.get('t_status')
                    if old_s != new_s:
                        if old_s == 1:#出库
                            ticket_outstore(pk)
                        elif old_s == 5:#出池
                            ticket_outpool(pk)
                        if new_s == 1:#入库
                            ticket_instore(pk)
                        elif new_s == 5:#入池
                            ticket_inpool(pk)
                        elif new_s == 5:#卖出
                            # ticket_outpool(pk)
                            instance.maichujiage = instance.piaomianjiage * (1 - instance.maichuhuilv)
                            instance.lirun = instance.maichujiage - instance.gourujiage
                            pass

                    pass
                if 'pay_status' in form.changed_data:
                    if form.cleaned_data.get('pay_status') == 2:
                        ticket_pay(pk)
                    pass
                if 'sell_status' in form.changed_data:
                    if form.cleaned_data.get('sell_status') == 2:
                        ticket_sold(pk)
                    pass
                instance.save()
                message = None
                # return render(request, 'ticket/ticket_edit.html', locals())
                return redirect('ticket_edit', pk=pk)

    else:
        form = TicketEditForm(request.POST or None, instance=ticket_ins)

    form.fields['qianpaipiaohao'].disabled = True
    form.fields['piaohao'].disabled = True
    form.fields['chupiaohang'].disabled = True
    form.fields['chupiaoriqi'].disabled = True
    form.fields['daoqiriqi'].disabled = True
    form.fields['gongyingshang'].disabled = True
    form.fields['gouruhuilv'].disabled = True
    form.fields['piaomianjiage'].disabled = True
    form.fields['gourujiage'].disabled = True
    form.fields['gouruzijinchi'].disabled = True
    form.fields['gourucard'].disabled = True
    if (not message) and ticket_ins.pay_status == 2:
        form.fields['pay_status'].disabled = True
    if (not message) and ticket_ins.sell_status == 4:
        form.fields['sell_status'].disabled = True
    if (not message) and ticket_ins.t_status == 3:
        form.fields['t_status'].disabled = True
        form.fields['maichulilv'].disabled = True
        form.fields['maichujiage'].disabled = True
        form.fields['maichucard'].disabled = True
        form.fields['maipiaoren'].disabled = True
    form.fields['lirun'].disabled = True
    return render(request, 'ticket/ticket_edit.html', locals())
def ticket_index(request,  pk):
    ticket_ins = get_object_or_404(Ticket, pk=pk)
    fee_data = Fee.objects.filter(ticket=pk).order_by('-pub_date')
    data_list, page_range, count, page_nums = pagination(request, fee_data)


    form = TicketEditForm(request.POST or None, instance=ticket_ins)
    feeform = TicketFeeForm(request.POST or None)
    if request.method == 'POST':
        if feeform.is_valid():
            instance = feeform.save(commit=False)
            instance.ticket = Ticket.objects.get(id = pk)
            instance.save()
            instance.yinhangka.money = instance.yinhangka.money - instance.money * 2
            # instance.yinhangka.save()
            redirect('ticket_index',pk=pk)

    for m in form.fields:
        form.fields[m].disabled = True
    return render(request, 'ticket/ticket_index.html', locals())

#显示各列表信息
@login_required
def ticket_list(request):
    #从根据不同的请求，来获取相应的数据,并跳转至相应页面

    # 将原先的data更名为raw_data
    raw_data = Ticket.objects.all().order_by('-goumairiqi')
    print(raw_data)
    list_template = 'ticket/ticket_list.html'

    #通过GET方法从提交的URL来获取相应参数
    if request.method == 'GET':
        #建立一个空的参数的字典
        kwargs = {}
        #建立一个空的查询语句
        query = ''
        #提交过来的GET值是一个迭代的键值对
        for key in request.GET.keys():
            value = request.GET.getlist(key)
            #刨去其中的token和page选项
            if key != 'csrfmiddlewaretoken' and key != 'page':
                #由于线路和设备的外键均与node表格有关，当查询线路中的用户名称或设备信息中的使用部门时，可以直接通过以下方式跨表进行查找
                if key == 'node':
                    kwargs['node__node_name__contains'] = value
                    #该query用于页面分页跳转时，能附带现有的搜索条件
                    query += '&' + key + '=' + value
                #其余的选项均通过key来辨别
                else:
                    kwargs[key + '__contains'] = value
                    #该query用于页面分页跳转时，能附带现有的搜索条件
                    query += '&' + key + '=' + value
        #通过元始数据进行过滤，过滤条件为健对值的字典
        data = raw_data.filter(**kwargs)
    #如果没有从GET提交中获取信息，那么data则为元始数据
    else:
        data = raw_data
    print(data)

    #将分页的信息传递到展示页面中去
    data_list, page_range, count, page_nums = pagination(request, data)
    #建立context字典，将值传递到相应页面
    context = {
        'data': data_list,
        'query': query,
        'page_range': page_range,
        'count': count,
        'page_nums': page_nums,
    }
    print(context)
    #跳转到相应页面，并将值传递过去
    return render(request,list_template,context)

def ticket_import(request):
    context = {}
    # 如果form通过POST方法发送数据
    if request.method == 'GET':
        stamp = request.GET.get('stamp')
        items = TicketsImport.objects.filter(stamp=stamp)
    if request.method == "POST":
        if 'upfile' in request.POST.keys():
            stamp = uuid.uuid1()
            path = '\\csvs\\'  # 上传文件的保存路径，可以自己指定任意的路径
            if not os.path.exists(path):
                os.makedirs(path)
            with open(path + 'tmp.csv', 'wb+')as destination:
                for chunk in request.FILES['file'].chunks():
                    destination.write(chunk)
            csv_reader = csv.reader(open(path + 'tmp.csv', 'r', newline=''))
            for row in csv_reader:
                a = len(row)
                if len(row) == 14:
                    if row[5].startswith('2'):
                        m = TicketsImport()
                        m.stamp = stamp
                        m.piaohao = row[0]
                        m.chupiaoren = row[1]
                        m.shoukuanren = row[2]
                        m.piaomianjiage = float(row[3].replace(',',''))
                        m.piaomianlixi = row[4]
                        m.chupiaoriqi = row[5].replace(' ','').replace('\t','')
                        m.daoqiriqi = row[6].replace(' ','').replace('\t','')
                        m.leixing = row[7]
                        m.zhuangtai = row[8]
                        m.chupiaohang = row[9]
                        m.chupiaohangb = row[10]
                        m.chengduiren = row[11]
                        m.shoupiaoren = row[12]
                        m.shoupiaohang = row[13]
                        m.save()
                        print(row)

            return redirect('%s?stamp=%s' % (reverse('ticket_import'),stamp))
        elif 'savefile' in request.POST.keys():
            stamp = request.GET.get('stamp')
            print(stamp)
            TicketsImport.objects.filter(stamp=stamp).update(saved=True)
            items = TicketsImport.objects.filter(stamp=stamp)
            for item in items:
                m = Ticket()
                m.piaohao = item.piaohao
                m.chupiaohang = item.chupiaohang
                m.chupiaoriqi = item.chupiaoriqi
                m.daoqiriqi = item.daoqiriqi
                m.piaomianjiage = item.piaomianjiage
                m.gongyingshang = item.chupiaoren
                m.save()
                pass

            return redirect('ticket_list')
            pass
        # return redirect('ticket_import',)

    # 如果是通过GET方法请求数据，返回一个空的表单
    # else:
        # form = NameForm()
    # context['forma'] = form
    return render(request, 'ticket/ticket_import.html',  locals())


def handle_upload_file(file):
    path = '\\csvs\\'  # 上传文件的保存路径，可以自己指定任意的路径
    if not os.path.exists(path):
        os.makedirs(path)
    with open(path + 'tmp.csv', 'wb+')as destination:
        for chunk in file.chunks():
            destination.write(chunk)
    csv_reader = csv.reader(open(path + 'tmp.csv', 'r', newline=''))
    res = []
    for row in csv_reader:
        a = len(row)
        if len(row) == 14:
            if row[5].startswith('2'):
                m = Ticket()
                m.qianpaipiaohao = row[0]
                m.piaohao = row[0]
                m.chupiaohang = row[9]
                m.chupiaoriqi = row[5]
                m.daoqiriqi = row[6]
                m.piaomianjiage = row[3]
                res.append(m)
                print(row)

            pass
    return res


#显示各列表信息
@login_required
def card_list(request):
    #从根据不同的请求，来获取相应的数据,并跳转至相应页面

    # 将原先的data更名为raw_data
    raw_data = Card.objects.all()
    print(raw_data)
    list_template = 'ticket/card_list.html'
    sub_title = '银行卡信息'

    #通过GET方法从提交的URL来获取相应参数
    if request.method == 'GET':
        #建立一个空的参数的字典
        kwargs = {}
        #建立一个空的查询语句
        query = ''
        #提交过来的GET值是一个迭代的键值对
        for key in request.GET.keys():
            value = request.GET.getlist(key)
            #刨去其中的token和page选项
            if key != 'csrfmiddlewaretoken' and key != 'page':
                #由于线路和设备的外键均与node表格有关，当查询线路中的用户名称或设备信息中的使用部门时，可以直接通过以下方式跨表进行查找
                if key == 'node':
                    kwargs['node__node_name__contains'] = value
                    #该query用于页面分页跳转时，能附带现有的搜索条件
                    query += '&' + key + '=' + value
                #其余的选项均通过key来辨别
                else:
                    kwargs[key + '__contains'] = value
                    #该query用于页面分页跳转时，能附带现有的搜索条件
                    query += '&' + key + '=' + value
        #通过元始数据进行过滤，过滤条件为健对值的字典
        data = raw_data.filter(**kwargs)
    #如果没有从GET提交中获取信息，那么data则为元始数据
    else:
        data = raw_data
    print(data)

    #将分页的信息传递到展示页面中去
    data_list, page_range, count, page_nums = pagination(request, data)
    #建立context字典，将值传递到相应页面
    context = {
        'data': data_list,
        'query': query,
        'page_range': page_range,
        'count': count,
        'edit_url':'',
        'page_nums': page_nums,
        'page_title': '基础资料',
        'sub_title': sub_title,
    }
    print(context)
    #跳转到相应页面，并将值传递过去
    return render(request,list_template,context)
#增加
def card_add(request):
    #从TaskForm获取相关信息
    form = CardForm(request.POST or None)
    if form.is_valid():
        instance = form.save(commit=False)
        instance.money = 0
        instance.save()
        return redirect('card_list',)


    context = {
        'form': form,
        'page_title': '银行卡处理',
        'sub_title': '新建银行卡',
        'sub_title': '新建银行卡',
    }
    return render(request, 'ticket/card_add.html',  context)

#修改数据,函数中的pk代表数据的id
def card_edit(request,  pk):
    card_ins = get_object_or_404(Card, pk=pk)
    fee_data = Fee.objects.filter(yinhangka=pk).order_by('-pub_date')
    data_list, page_range, count, page_nums = pagination(request, fee_data)

    card_total = [card_ins.money,]
    card_date = ['现在',]
    for i in range(len(fee_data)):
        list.insert(card_total, 0, card_total[0] - fee_data[i].money)
        list.insert(card_date, 0, fee_data[i].pub_date)
    sub_title = '修改银行卡信息'
    if request.method == 'POST':
        #任务联系人为可编辑选项，并填充原先的任务联系人
        card_ins.name = request.POST['name']
        card_ins.beizhu = request.POST['beizhu']

        card = Card.objects.get(id = card_ins.id)
        if request.POST['fee'].strip(' ') != '':
            fee_ins = Fee()
            fee_ins.yinhangka = card
            fee_ins.money = float(request.POST['fee'])
            fee_ins.name = request.POST['feebeizhu'].strip(' ')
            fee_ins.save()
            card_ins.money = card_ins.money + fee_ins.money
        card_ins.save()

        return redirect('card_edit', pk=card.id)

    context = {
        'data': data_list,
        'item': card_ins,
        'card_total': card_total,
        'card_date': card_date,
        'page_range': page_range,
        'count': count,
        'page_nums': page_nums,
        'page_title': '基础资料',
        'sub_title': sub_title,
    }
    #与res_add.html用同一个页面，只是edit会在res_add页面做数据填充
    return render(request, 'ticket/card_edit.html', context)
def pool_dash(request):
    pool = Pool.objects.last()
    pool_data = Pool.objects.all().order_by('-pub_date')
    data_list, page_range, count, page_nums = pagination(request, pool_data)
    form = PoolForm(request.POST or None)
    form.fields['card'].required = True

    count_t = Ticket.objects.filter(t_status=5).count()
    sum_money = 0
    print(count_t)
    if count_t > 0:
        sum_money = Ticket.objects.filter(t_status=5).values('t_status').annotate(sum_money=Sum('piaomianjiage')).values('sum_money')[0].get('sum_money')
        print(str(Ticket.objects.filter(t_status=5).values('t_status').annotate(sum_money=Sum('piaomianjiage')).values('sum_money').query))
        print(sum_money)
    if request.method == 'POST':
        if form.is_valid():
            # 创建实例，需要做些数据处理，暂不做保存
            pool = form.save(commit=False)
            p = Pool.objects.last()
            if not p:
                p = Pool()
            money = pool.money
            if form.cleaned_data.get('p_status') == '4':
                card_fee(pool.card.pk, money, '从保证金提取')
                money = 0 - money
                pool.pool_status = 4
            else:
                card_fee(pool.card.pk, 0-money,'充值到保证金')
                pool.pool_status = 3

            pool.totalmoney = p.totalmoney + money
            pool.promoney = p.promoney + money
            pool.unusemoney = p.unusemoney + money
            pool.usedmoney = p.usedmoney
            pool.money = money
            pool.save()
            return redirect('pool_dash')
        pass

    context = {
        'data': data_list,
        'sum_money': sum_money,
        'count_t': count_t,
        'item': pool,
        'page_range': page_range,
        'count': count,
        'page_nums': page_nums,
        'form':form,
    }
    #与res_add.html用同一个页面，只是edit会在res_add页面做数据填充
    return render(request, 'ticket/pool_dash.html', context)

def pool_pro(request):
    pool = Pool.objects.last()
    pool_data = Pool.objects.all().order_by('-pub_date')
    data_list, page_range, count, page_nums = pagination(request, pool_data)

    count_t = Ticket.objects.filter(t_status=5).count()
    sum_money = 0
    print(count_t)
    if count_t > 0:
        sum_money = Ticket.objects.filter(t_status=5).values('t_status').annotate(sum_money=Sum('piaomianjiage')).values('sum_money')[0].get('sum_money')
        print(str(Ticket.objects.filter(t_status=5).values('t_status').annotate(sum_money=Sum('piaomianjiage')).values('sum_money').query))
        print(sum_money)
    if request.method == 'POST':
        # #任务联系人为可编辑选项，并填充原先的任务联系人
        # card_ins.name = request.POST['name']
        # card_ins.beizhu = request.POST['beizhu']
        #
        # card = Card.objects.get(id = card_ins.id)
        # if request.POST['fee'].strip(' ') != '':
        #     fee_ins = Fee()
        #     fee_ins.yinhangka = card
        #     fee_ins.money = float(request.POST['fee'])
        #     fee_ins.name = request.POST['feebeizhu'].strip(' ')
        #     fee_ins.save()
        #     card_ins.money = card_ins.money + fee_ins.money
        # card_ins.save()

        # return redirect('card_edit', pk=card.id)
        pass

    context = {
        'data': data_list,
        'sum_money': sum_money,
        'count_t': count_t,
        'item': pool,
        'page_range': page_range,
        'count': count,
        'page_nums': page_nums,
    }
    #与res_add.html用同一个页面，只是edit会在res_add页面做数据填充
    return render(request, 'ticket/pool_dash.html', context)
#配置
def inpoolPercent(request):
    item = InpoolPercent.objects.last()
    if not item:
        item = InpoolPercent()
        item.inpoolPer = 100
        item.save()
    items_data = InpoolPercent.objects.all().order_by('-pub_date')
    data_list, page_range, count, page_nums = pagination(request, items_data)
    # form = PoolForm(request.POST or None)
    # form.fields['card'].required = True
    items_total = []
    items_date = []
    for i in range(len(items_data)):
        list.insert(items_total, 0, items_data[i].inpoolPer)
        list.insert(items_date, 0, items_data[i].pub_date)

    if request.method == 'POST':
        temp = InpoolPercent()
        temp.inpoolPer = request.POST['inpoolPer']
        temp.save()
        return redirect('inpoolPercent')
        pass

    context = {
        'data': data_list,
        'item': item,
        'items_total': items_total,
        'items_date': items_date,
        'page_range': page_range,
        'count': count,
        'page_nums': page_nums,
    }
    #与res_add.html用同一个页面，只是edit会在res_add页面做数据填充
    return render(request, 'ticket/inpoolPer.html',  context)

#分页函数
def pagination(request, queryset, display_amount=10, after_range_num = 5,before_range_num = 4):
    #按参数分页

    try:
        #从提交来的页面获得page的值
        page = int(request.GET.get("page", 1))
        #如果page值小于1，那么默认为第一页
        if page < 1:
            page = 1
    #若报异常，则page为第一页
    except ValueError:
            page = 1
    #引用Paginator类
    paginator = Paginator(queryset, display_amount)
    #总计的数据条目
    count = paginator.count
    #合计页数
    num_pages = paginator.num_pages



    try:
        #尝试获得分页列表
        objects = paginator.page(page)
    #如果页数不存在
    except EmptyPage:
        #获得最后一页
        objects = paginator.page(paginator.num_pages)
    #如果不是一个整数
    except PageNotAnInteger:
        #获得第一页
        objects = paginator.page(1)
    #根据参数配置导航显示范围
    temp_range = paginator.page_range

    #如果页面很小
    if (page - before_range_num) <= 0:
        #如果总页面比after_range_num大，那么显示到after_range_num
        if temp_range[-1] > after_range_num:
            page_range = range(1, after_range_num+1)
        #否则显示当前页
        else:
            page_range = range(1, temp_range[-1]+1)
    #如果页面比较大
    elif (page + after_range_num) > temp_range[-1]:
        #显示到最大页
        page_range = range(page-before_range_num,temp_range[-1]+1)
    #否则在before_range_num和after_range_num之间显示
    else:
        page_range = range(page-before_range_num+1, page+after_range_num)
    #返回分页相关参数
    return objects, page_range, count, num_pages
