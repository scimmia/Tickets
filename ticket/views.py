import csv
import datetime
import json
import os
import time
import uuid

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Sum, Count, Q
from django.shortcuts import render, redirect, get_object_or_404

from django.contrib.auth import views
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
# Create your views here.
from django.urls import reverse

from ticket.filters import TicketFilter
from ticket.forms import TicketForm, CardForm, TicketEditForm, PoolForm, TicketFeeForm, TicketOrderFeeForm, \
    SuperLoanForm, LoanForm
from ticket.models import Card, Fee, Ticket, Order, StoreFee, PoolFee, Pool, InpoolPercent, TicketsImport, \
    StoreTicketsImport, SuperLoan, Loan_Order


@login_required
def dashboard(request):
    ts = Ticket.objects.values('t_status','t_type').annotate(t_count = Count('id'),sum_money=Sum('piaomianjiage'))
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
                kuzhis = round(t['sum_money'],2)
                pass
            elif t['t_type'] == 2:
                kudianc = t['t_count']
                kudians = round(t['sum_money'],2)
                pass
        elif t['t_status'] == 5:
            if t['t_type'] == 1:
                chizhic = t['t_count']
                chizhis = round(t['sum_money'],2)
                pass
            elif t['t_type'] == 2:
                chidianc = t['t_count']
                chidians = round(t['sum_money'],2)
                pass
        pass
    kuc = kudianc + kuzhic
    kus = kudians + kuzhis
    chic = chidianc + chizhic
    chis = chidians + chizhis
    allc = kuc + chic
    alls = kus + chis
    print(ts)
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

def ticket_poolpay(ticket_pk):
    ticket = Ticket.objects.get(pk=ticket_pk)
    p = Pool.objects.last()
    if not p:
        p = Pool()
    pool = Pool()
    pool.totalmoney = p.totalmoney
    pool.promoney = p.promoney
    pool.unusemoney = p.unusemoney - ticket.gourujiage
    pool.usedmoney = p.usedmoney + ticket.gourujiage
    pool.ticket = ticket
    pool.money = 0 - ticket.gourujiage
    pool.pool_status = 5
    pool.save()

def card_fee(card_pk,money,name,fee_type):
    card = Card.objects.get(pk=card_pk)
    fee_ins = Fee()
    fee_ins.yinhangka = card
    fee_ins.money = money
    fee_ins.name = name
    fee_ins.fee_type = fee_type
    fee_ins.save()
    card.money = card.money + fee_ins.money
    card.save()
    return fee_ins

#增加
def ticket_add(request):
    form = TicketForm(request.POST or None)
    #从TaskForm获取相关信息
    context = {
        'form': form,
        'gongyingshang': get_ticketlists('gongyingshang'),
        'chupiaohang': get_ticketlists('chupiaohang'),
    }
    if form.is_valid():
        times = 1
        if form.cleaned_data.get('fenshu') and form.cleaned_data.get('fenshu')>1:
            times = form.cleaned_data.get('fenshu')
        instance = form.save(commit=False)
        counter = 1
        while counter <= times:
            counter += 1
            instance.pk = None
            instance.save()
            if instance.t_status == 1:
                ticket_instore(instance.pk)
            elif instance.t_status == 5:
                ticket_inpool(instance.pk)

            if instance.gouruzijinchi:
                ticket_poolpay(instance.pk)
                instance.pay_status = 2
                instance.save()
                pass
        # return render(request, 'ticket/ticket_add.html',locals())
        return redirect('ticket_list')
    else:
        return render(request, 'ticket/ticket_add.html',context)
def ticket_index(request,  pk):
    ticket_ins = get_object_or_404(Ticket, pk=pk)
    form = TicketEditForm(request.POST or None, instance=ticket_ins)

    for m in form.fields:
        form.fields[m].disabled = True
    return render(request, 'ticket/ticket_index.html', locals())
def ticket_fix(request):
    if request.method == 'POST':
        pk = request.POST['t_id']
        t = Ticket.objects.get(pk = pk)
        t.gourujiage = float(request.POST['t_gourujiage'])
        t.save()
        return redirect('ticket_index',pk)
    return redirect('ticket_list')

def get_ticketlists(col):
    gys = Ticket.objects.values(col).annotate(Count('id'))
    t = []
    for g in gys:
        list.insert(t,0,g[col])
    return t


#显示各列表信息
@login_required
def ticket_list(request):
    #从根据不同的请求，来获取相应的数据,并跳转至相应页面
    if request.method == 'POST':
        if 'all_tostore' in request.POST.keys():
            print('all_tostore')
            ids = request.POST['ids']
            if len(ids) > 0:
                tickets = Ticket.objects.filter(id__in=ids.split(','))
                for t in tickets:
                    if t.t_status == 5:
                        t.t_status = 1
                        t.save()
                        ticket_outpool(t.pk)
                        ticket_instore(t.pk)
            pass
        elif 'all_topool' in request.POST.keys():
            print('all_topool')
            ids = request.POST['ids']
            if len(ids) > 0:
                tickets = Ticket.objects.filter(id__in=ids.split(','))
                for t in tickets:
                    if t.t_status == 1:
                        t.t_status = 5
                        t.save()
                        ticket_outstore(t.pk)
                        ticket_inpool(t.pk)
            pass
    # 将原先的data更名为raw_data
    raw_data = Ticket.objects.all().order_by('-goumairiqi')
    print(raw_data)
    list_template = 'ticket/ticket_list.html'

    #通过GET方法从提交的URL来获取相应参数
    #建立一个空的参数的字典
    kwargs = {}
    #建立一个空的查询语句
    query = ''
    #提交过来的GET值是一个迭代的键值对
    for key in request.GET.keys():
        value = request.GET[(key)]
        print(key,value)
        #刨去其中的token和page选项
        if key != 'csrfmiddlewaretoken' and key != 'page' and (len(value)>0):
            #由于线路和设备的外键均与node表格有关，当查询线路中的用户名称或设备信息中的使用部门时，可以直接通过以下方式跨表进行查找
            if key == 'node':
                kwargs['node__node_name__contains'] = value
                #该query用于页面分页跳转时，能附带现有的搜索条件
                query += '&' + key + '=' + value
            #其余的选项均通过key来辨别
            else:
                kwargs[key] = value
                #该query用于页面分页跳转时，能附带现有的搜索条件
                query += '&' + key + '=' + value
    #通过元始数据进行过滤，过滤条件为健对值的字典
    data = raw_data.filter(**kwargs)
    #如果没有从GET提交中获取信息，那么data则为元始数据

    #将分页的信息传递到展示页面中去
    data_list, page_range, count, page_nums = pagination(request, data)
    #建立context字典，将值传递到相应页面
    context = {
        'data': data_list,
        'gongyingshang': get_ticketlists('gongyingshang'),
        'maipiaoren': get_ticketlists('maipiaoren'),
        'query': query,
        'page_range': page_range,
        'count': count,
        'page_nums': page_nums,
        'filter': filter,
    }
    print(context)
    #跳转到相应页面，并将值传递过去
    return render(request,list_template,context)

@login_required
def tickets_needfix(request):
    raw_data = Ticket.objects.filter(pay_status=1,payorder=None,gourujiage=0).order_by('-goumairiqi')
    print(raw_data)
    list_template = 'ticket/tickets_needfix.html'
    context = {
        'data': raw_data,
    }
    print(context)
    #跳转到相应页面，并将值传递过去
    return render(request,list_template,context)

def ticket_needselect(request,index):

    if index == 1:
        title = '付款'
        raw_data = Ticket.objects.filter(pay_status=1,payorder=None,gourujiage__gt=0).order_by('-goumairiqi')
    else:
        title = '收款'
        raw_data = Ticket.objects.filter(sell_status=3,sellorder=None).order_by('-goumairiqi')
    list_template = 'ticket/ticket_toselect.html'

    #通过GET方法从提交的URL来获取相应参数
    if request.method == 'GET':
        #建立一个空的参数的字典
        kwargs = {}
        #建立一个空的查询语句
        for key in request.GET.keys():
            value = request.GET[(key)]
            if key != 'csrfmiddlewaretoken' and key != 'page' and (len(value)>0):
                kwargs[key] = value
        #通过元始数据进行过滤，过滤条件为健对值的字典
        data = raw_data.filter(**kwargs)
    #如果没有从GET提交中获取信息，那么data则为元始数据
    else:
        data = raw_data

    #建立context字典，将值传递到相应页面
    context = {
        'data': data,
        'index': index,
        'title': title,
    }
    print(context)
    #跳转到相应页面，并将值传递过去
    return render(request,list_template,context)

def ticket_needpay(request):
    return ticket_needselect(request,1)
def ticket_needcollect(request):
    return ticket_needselect(request,3)

def ticket_orderlist(request,index):
    #从根据不同的请求，来获取相应的数据,并跳转至相应页面
    if index == 1:
        list_template = 'ticket/ticket_payorders.html'
    else:
        list_template = 'ticket/ticket_sellorders.html'
    raw_data = Order.objects.filter(order_type=index).order_by('-pub_date')
    context = {
        'data': raw_data,
    }
    return render(request,list_template,context)
def ticket_payorders(request):
    return ticket_orderlist(request,1)
def ticket_sellorders(request):
    return ticket_orderlist(request,2)

def ticket_topay(request):
    context = {}
    list_template = 'ticket/ticket_topay.html'
    if request.method == 'POST':
        feeform = TicketFeeForm()
        index = request.POST['index']
        ids = request.POST['ids']
        selected_num = request.POST['selected_num']
        selected_piaomian = request.POST['selected_piaomian']
        selected_real = request.POST['selected_real']
        if index == '1':
            title = '付款'
        else:
            title = '收款'
        raw_data = Ticket.objects.filter(id__in=ids.split(',')).order_by('-goumairiqi')
        #建立context字典，将值传递到相应页面
        context = {
            'data': raw_data,
            'index': index,
            'ids': ids,
            'title': title,
            'feeform': feeform,
            'selected_num': selected_num,
            'selected_piaomian': selected_piaomian,
            'selected_real': selected_real,
        }
    print(context)
    #跳转到相应页面，并将值传递过去
    return render(request,list_template,context)
def ticket_tocollect(request):
    context = {}
    list_template = 'ticket/ticket_tocollect.html'
    if request.method == 'POST':
        feeform = TicketFeeForm()
        index = request.POST['index']
        ids = request.POST['ids']
        selected_num = request.POST['selected_num']
        selected_piaomian = request.POST['selected_piaomian']
        selected_real = request.POST['selected_real']
        title = '收款'
        raw_data = Ticket.objects.filter(id__in=ids.split(',')).order_by('-goumairiqi')
        prices = set([])
        for t in raw_data:
            prices.add(str(t.piaomianjiage))
            # if str(t.piaomianjiage) in items:
            #     items[str(t.piaomianjiage)].append(t.pk)
            # else:
            #     items[str(t.piaomianjiage)] = [t.pk]
        #建立context字典，将值传递到相应页面
        context = {
            'data': raw_data,
            'maipiaoren': get_ticketlists('maipiaoren'),
            'prices': prices,
            'index': index,
            'ids': ids,
            'title': title,
            'feeform': feeform,
            'selected_num': selected_num,
            'selected_piaomian': selected_piaomian,
            'selected_real': selected_real,
        }
    print(context)
    #跳转到相应页面，并将值传递过去
    return render(request,list_template,context)

def ticket_createorder(request):
    if request.method == 'POST':
        order = Order()
        order.order_type = int(request.POST['ordertype'])
        order.save()
        fees = json.loads(request.POST['fees'])
        for fee in fees:
            f = Fee()
            f.order = order
            f.fee_type = order.order_type
            f.name = fee['name']
            f.money = float(fee['money'])
            f.yinhangka = Card.objects.get(pk=(fee['cardid']))
            f.save()
            order.fee_sum = order.fee_sum+f.money
            order.fee_count = order.fee_count + 1

        ids = request.POST['ids']
        if order.order_type == 1:
            Ticket.objects.filter(id__in=ids.split(',')).update(pay_status =2,payorder=order,paytime=order.pub_date)
        elif order.order_type == 2:
            Ticket.objects.filter(id__in=ids.split(',')).update(sell_status = 4,sellorder=order,selltime=order.pub_date,maipiaoren = request.POST['maipiaoren'])

        tickets = Ticket.objects.filter(id__in=ids.split(',')).order_by('-goumairiqi')
        for t in tickets:
            order.ticket_count = order.ticket_count + 1
            order.ticket_sum = order.ticket_sum + t.piaomianjiage
            if order.order_type == 1:
                order.money = order.money + t.gourujiage
            elif order.order_type == 2:
                t.maichujiage = float(request.POST['maichujiage'+str(t.piaomianjiage)])
                t.save()
                order.money = order.money + int(request.POST['maichujiage'+str(t.piaomianjiage)])
            if t.gourujiage > 0 and t.maichujiage > 0:
                t.lirun = t.maichujiage - t.gourujiage
                t.save()
        order.total_sum = order.money + order.fee_sum
        order.payfee_sum = 0
        order.needpay_sum = order.total_sum - order.payfee_sum
        order.save()
        if order.order_type == 1:
            return redirect('ticket_payorder', pk=order.id)
        elif order.order_type == 2:
            return redirect('ticket_sellorder', pk=order.id)

        #建立context字典，将值传递到相应页面
    return redirect('ticket_payorder', pk=order.id)


def ticket_payorder(request,  pk):
    order_ins = get_object_or_404(Order, pk=pk)
    order = Order.objects.get(pk=pk)
    ticket_data = Ticket.objects.filter(payorder=pk).order_by('-goumairiqi')
    fee_data = Fee.objects.filter(order=pk,fee_type=1).order_by('-pub_date')
    payfee_data = Fee.objects.filter(Q(order=pk)&(Q(fee_type=3)|Q(fee_type=5)|Q(fee_type=7))).order_by('-pub_date')
    list_template = 'ticket/ticket_payorder.html'
    feeform = TicketOrderFeeForm(request.POST or None)
    # feeform.fields['money'].max_value = needpay_sum
    if request.method == 'POST':
        if feeform.is_valid():
            if feeform.cleaned_data.get('money')>order.needpay_sum:
                message = u'付款金额不能大于待支付金额'
            else:
                cardmoneyadd = False
                instance = feeform.save(commit=False)
                instance.order = order
                if feeform.cleaned_data.get('isOrderFee'):
                    if feeform.cleaned_data.get('fee_status') == '1':#收入
                        instance.fee_type = 7
                    elif feeform.cleaned_data.get('fee_status') == '2':#支出
                        instance.fee_type = 5
                        instance.money = -1 * instance.money
                else:
                    order.payfee_count = order.payfee_count + 1
                    order.payfee_sum = order.payfee_sum + instance.money
                    order.needpay_sum = order.total_sum - order.payfee_sum
                    order.save()
                    instance.fee_type = 3
                    instance.money = -1 * instance.money
                instance.save()
                instance.yinhangka.money = instance.yinhangka.money + instance.money
                instance.yinhangka.save()

                redirect('ticket_payorder',pk=pk)
    return render(request,list_template,locals())
def ticket_sellorder(request,  pk):
    order_ins = get_object_or_404(Order, pk=pk)
    order = Order.objects.get(pk=pk)
    ticket_data = Ticket.objects.filter(sellorder=pk).order_by('-goumairiqi')
    fee_data = Fee.objects.filter(order=pk,fee_type=2).order_by('-pub_date')
    payfee_data = Fee.objects.filter(Q(order=pk)&(Q(fee_type=4)|Q(fee_type=6)|Q(fee_type=8))).order_by('-pub_date')
    list_template = 'ticket/ticket_sellorder.html'
    feeform = TicketOrderFeeForm(request.POST or None)
    if request.method == 'POST':
        if feeform.is_valid():
            if feeform.cleaned_data.get('money')>order.needpay_sum:
                message = u'收款金额不能大于待收取金额'
            else:
                instance = feeform.save(commit=False)
                instance.order = order
                if feeform.cleaned_data.get('isOrderFee'):
                    if feeform.cleaned_data.get('fee_status') == '1':#收入
                        instance.fee_type = 8
                    elif feeform.cleaned_data.get('fee_status') == '2':#支出
                        instance.fee_type = 6
                        instance.money = -1 * instance.money
                else:
                    instance.fee_type = 4
                    order.payfee_count = order.payfee_count + 1
                    order.payfee_sum = order.payfee_sum + instance.money
                    order.needpay_sum = order.total_sum - order.payfee_sum
                    order.save()
                instance.save()
                instance.yinhangka.money = instance.yinhangka.money + instance.money
                instance.yinhangka.save()

                redirect('ticket_sellorder',pk=pk)
    return render(request,list_template,locals())
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
                m.gourujiage = item.piaomianjiage
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


def flow_import(request):
    context = {}
    # 如果form通过POST方法发送数据
    if request.method == 'GET':
        stamp = request.GET.get('stamp')
        items = StoreTicketsImport.objects.filter(stamp=stamp)
    if request.method == "POST":
        if 'upfile' in request.POST.keys():
            stamp = uuid.uuid1()
            path = '\\csvs\\'  # 上传文件的保存路径，可以自己指定任意的路径
            if not os.path.exists(path):
                os.makedirs(path)
            with open(path + 'tmp.csv', 'wb+')as destination:
                for chunk in request.FILES['file'].chunks():
                    destination.write(chunk)
            with open(path + 'tmp.csv', mode='r', encoding='utf-8', newline='') as f:
                # 此处读取到的数据是将每行数据当做列表返回的
                reader = csv.reader(f)
                for row in reader:
                    # 此时输出的是一行行的列表
                    # print(row)
                    a = len(row)
                    if len(row) == 10:
                        if row[0].startswith('2'):
                            m = StoreTicketsImport()
                            m.stamp = stamp
                            m.qianpaipiaohao = row[1]
                            m.piaohao = row[2]
                            m.maipiaoriqi = row[0].replace(' ','').replace('\t','').replace('/','-')
                            m.chupiaoren = row[9]
                            m.piaomianjiage = float(row[6].replace(',',''))
                            if row[7].isdigit():
                                m.piaomianlixi = float(row[7])
                            m.chupiaoriqi = row[4].replace(' ','').replace('\t','').replace('/','-')
                            m.daoqiriqi = row[5].replace(' ','').replace('\t','').replace('/','-')
                            m.leixing = '流水表'
                            m.chupiaohang = row[3]
                            m.save()
                            print(row)

            return redirect('%s?stamp=%s' % (reverse('flow_import'),stamp))
        elif 'savefile' in request.POST.keys():
            stamp = request.GET.get('stamp')
            print(stamp)
            StoreTicketsImport.objects.filter(stamp=stamp).update(saved=True)
            items = StoreTicketsImport.objects.filter(stamp=stamp)
            for item in items:
                m = Ticket()
                m.qianpaipiaohao = item.qianpaipiaohao
                m.piaohao = item.piaohao
                m.chupiaohang = item.chupiaohang
                m.chupiaoriqi = item.chupiaoriqi
                m.daoqiriqi = item.daoqiriqi
                m.piaomianjiage = item.piaomianjiage
                m.gourujiage = item.piaomianjiage - item.piaomianlixi
                m.pay_status = 2
                m.gongyingshang = item.chupiaoren
                m.save()
                m.goumairiqi = item.maipiaoriqi
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

def pool_import(request):
    context = {}
    # 如果form通过POST方法发送数据
    if request.method == 'GET':
        stamp = request.GET.get('stamp')
        items = StoreTicketsImport.objects.filter(stamp=stamp)
    if request.method == "POST":
        if 'upfile' in request.POST.keys():
            stamp = uuid.uuid1()
            path = '\\csvs\\'  # 上传文件的保存路径，可以自己指定任意的路径
            if not os.path.exists(path):
                os.makedirs(path)
            with open(path + 'tmp.csv', 'wb+')as destination:
                for chunk in request.FILES['file'].chunks():
                    destination.write(chunk)
            with open(path + 'tmp.csv', mode='r', encoding='utf-8', newline='') as f:
                # 此处读取到的数据是将每行数据当做列表返回的
                reader = csv.reader(f)
                for row in reader:
                    # 此时输出的是一行行的列表
                    # print(row)
                    a = len(row)
                    if len(row) == 10:
                        if row[0].startswith('2'):
                            m = StoreTicketsImport()
                            m.stamp = stamp
                            m.qianpaipiaohao = row[1]
                            m.piaohao = row[2]
                            m.maipiaoriqi = row[0].replace(' ','').replace('\t','').replace('/','-')
                            m.chupiaoren = row[9]
                            m.piaomianjiage = float(row[6].replace(',',''))
                            m.piaomianlixi = m.piaomianjiage - float(row[8].replace(',',''))
                            m.chupiaoriqi = row[4].replace(' ','').replace('\t','').replace('/','-')
                            m.daoqiriqi = row[5].replace(' ','').replace('\t','').replace('/','-')
                            m.leixing = '流水表'
                            m.chupiaohang = row[3]
                            m.save()
                            print(row)

            return redirect('%s?stamp=%s' % (reverse('pool_import'),stamp))
        elif 'savefile' in request.POST.keys():
            stamp = request.GET.get('stamp')
            print(stamp)
            StoreTicketsImport.objects.filter(stamp=stamp).update(saved=True)
            items = StoreTicketsImport.objects.filter(stamp=stamp)
            for item in items:
                m = Ticket()
                m.qianpaipiaohao = item.qianpaipiaohao
                m.piaohao = item.piaohao
                m.chupiaohang = item.chupiaohang
                m.chupiaoriqi = item.chupiaoriqi
                m.daoqiriqi = item.daoqiriqi
                m.piaomianjiage = item.piaomianjiage
                m.gourujiage = item.piaomianjiage - item.piaomianlixi
                m.pay_status = 2
                m.t_status = 5
                m.gongyingshang = item.chupiaoren
                m.save()
                m.goumairiqi = item.maipiaoriqi
                m.save()
                ticket_inpool(m.pk)
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
    raw_data = Card.objects.all()
    print(raw_data)
    list_template = 'ticket/card_list.html'

    #将分页的信息传递到展示页面中去
    data_list, page_range, count, page_nums = pagination(request, raw_data)
    #建立context字典，将值传递到相应页面
    context = {
        'data': data_list,
        'page_range': page_range,
        'count': count,
        'edit_url':'',
        'page_nums': page_nums,
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
            fee_ins.fee_type = 11
            if request.POST['p_status'] == '4':#银行卡取出
                fee_ins.money = -1 * fee_ins.money
                fee_ins.fee_type = 12
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


def loan_orderlist(request,index):
    #从根据不同的请求，来获取相应的数据,并跳转至相应页面
    if index == 3:
        isloan = False
    else:
        isloan = True
    list_template = 'ticket/loan_orders.html'

    loanform = LoanForm(request.POST or None)
    if request.method == 'POST':
        if loanform.is_valid():
            instance = loanform.save(commit=False)
            instance.order_type = index
            instance.money_total = loanform.cleaned_data.get('money_benjin')+loanform.cleaned_data.get('money_lixi')
            instance.needpay_sum = loanform.cleaned_data.get('money_benjin')+loanform.cleaned_data.get('money_lixi')
            instance.save()
            if index == 3:
                fee = card_fee(instance.yinhangka.pk, 0 - loanform.cleaned_data.get('money_benjin'), '借款给他人',41)
                fee.loanorder = instance
                fee.save()
                return redirect('borrow_list')
            else:
                fee = card_fee(instance.yinhangka.pk, loanform.cleaned_data.get('money_benjin'), '从他人处贷款',42)
                fee.loanorder = instance
                fee.save()
                return redirect('loan_list')
            pass
    raw_data = Loan_Order.objects.filter(order_type=index).order_by('-pub_date')
    context = {
        'data': raw_data,
        'isloan': isloan,
        'loanform': loanform,
    }
    return render(request,list_template,context)
def borrow_list(request):
    return loan_orderlist(request,3)
def loan_list(request):
    return loan_orderlist(request,4)
def loanorder(request,  pk):
    order = Loan_Order.objects.get(pk=pk)
    payfee_data = Fee.objects.filter(Q(loanorder=pk)&(Q(fee_type=40 + order.order_type)|Q(fee_type=42 + order.order_type)|Q(fee_type=44 + order.order_type))).order_by('-pub_date')
    list_template = 'ticket/loan_order.html'
    feeform = TicketOrderFeeForm(request.POST or None)
    if request.method == 'POST':
        if feeform.is_valid():
            if feeform.cleaned_data.get('money')>order.needpay_sum and (not feeform.cleaned_data.get('isOrderFee')):
                message = u'收款金额不能大于待收取金额'
            else:
                instance = feeform.save(commit=False)
                instance.loanorder = order
                # if order.order_type == 3:#收借款
                #     if feeform.cleaned_data.get('isOrderFee'):
                #         if feeform.cleaned_data.get('fee_status') == '1':  # 收入
                #             instance.fee_type = 47
                #         elif feeform.cleaned_data.get('fee_status') == '2':  # 支出
                #             instance.fee_type = 45
                #             instance.money = -1 * instance.money
                #     else:
                #         instance.fee_type = 43
                #         order.payfee_count = order.payfee_count + 1
                #         order.payfee_sum = order.payfee_sum + instance.money
                #         order.needpay_sum = order.total_sum - order.payfee_sum
                #         order.save()
                # elif order.order_type == 4:#还贷款
                #     if feeform.cleaned_data.get('isOrderFee'):
                #         if feeform.cleaned_data.get('fee_status') == '1':  # 收入
                #             instance.fee_type = 48
                #         elif feeform.cleaned_data.get('fee_status') == '2':  # 支出
                #             instance.fee_type = 46
                #             instance.money = -1 * instance.money
                #     else:
                #         order.payfee_count = order.payfee_count + 1
                #         order.payfee_sum = order.payfee_sum + instance.money
                #         order.needpay_sum = order.total_sum - order.payfee_sum
                #         order.save()
                #         instance.fee_type = 44
                #         instance.money = -1 * instance.money

                if feeform.cleaned_data.get('isOrderFee'):
                    if feeform.cleaned_data.get('fee_status') == '1':  # 收入
                        instance.fee_type = 44+order.order_type
                    elif feeform.cleaned_data.get('fee_status') == '2':  # 支出
                        instance.fee_type = 42+order.order_type
                        instance.money = -1 * instance.money
                else:
                    instance.fee_type = 40+order.order_type
                    order.payfee_count = order.payfee_count + 1
                    order.payfee_sum = order.payfee_sum + instance.money
                    order.needpay_sum = order.needpay_sum - instance.money
                    order.save()
                    if order.order_type == 4:  # 还贷款
                        instance.money = -1 * instance.money

                instance.save()
                instance.yinhangka.money = instance.yinhangka.money + instance.money
                instance.yinhangka.save()

                return redirect('loanorder',pk=pk)
    return render(request,list_template,locals())

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
                card_fee(pool.card.pk, money, '从保证金提取',21)
                money = 0 - money
                pool.pool_status = 4
            else:
                card_fee(pool.card.pk, 0-money,'充值到保证金',22)
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


def loan_create(loan):
    p = Pool.objects.last()
    if not p:
        p = Pool()
    pool = Pool()
    pool.totalmoney = p.totalmoney - loan.money
    pool.promoney = p.promoney
    pool.unusemoney = p.unusemoney - loan.money
    pool.usedmoney = p.usedmoney
    pool.loan = loan
    pool.money = 0 - loan.money
    pool.pool_status = 6
    pool.save()
    pass
def loan_repay(loan):
    p = Pool.objects.last()
    if not p:
        p = Pool()
    pool = Pool()
    pool.totalmoney = p.totalmoney + loan.money
    pool.promoney = p.promoney
    pool.unusemoney = p.unusemoney + loan.money
    pool.usedmoney = p.usedmoney
    pool.loan = loan
    pool.money = loan.money
    pool.pool_status = 7
    pool.save()
    pass
def loan_promoneypay(loan):
    p = Pool.objects.last()
    if not p:
        p = Pool()
    pool = Pool()
    pool.totalmoney = p.totalmoney - loan.money
    pool.promoney = p.promoney - loan.money
    pool.unusemoney = p.unusemoney
    pool.usedmoney = p.usedmoney
    pool.loan = loan
    pool.money = 0 - loan.money
    pool.pool_status = 8
    pool.save()
    pass

def pool_loan(request):
    loan_data = SuperLoan.objects.all().order_by('-pub_date')
    card_data = Card.objects.all()

    form = SuperLoanForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            loan = SuperLoan()
            loan.name = form.cleaned_data.get('name')
            loan.money = form.cleaned_data.get('money')
            loan.save()
            loan_create(loan)
            return redirect('pool_loan')

    context = {
        'data': loan_data,
        'card_data': card_data,
        'form':form,
    }
    #与res_add.html用同一个页面，只是edit会在res_add页面做数据填充
    return render(request, 'ticket/pool_superloan.html', context)

def pool_loan_repay(request):
    if request.method == 'POST':
        ids = request.POST['ids']
        if len(ids) > 0:
            loans = SuperLoan.objects.filter(id__in=ids.split(','))

            for t in loans:
                if not t.isfinished:
                    t.isfinished = True
                    if 'all_pool' in request.POST.keys():
                        t.ispoolrepay = True
                        loan_promoneypay(t)
                    elif 'all_card' in request.POST.keys():
                        t.ispoolrepay = False
                        t.yinhangka = Card.objects.get(id = int(request.POST['yinhangka']))
                        fee = card_fee(t.yinhangka.pk,0-t.money,'还超短贷',31)
                        fee.superloan = t
                        fee.save()
                    t.repay_date = datetime.datetime.now()
                    t.save()
                    loan_repay(t)

        return redirect('pool_loan')
    return redirect('pool_loan')


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
