from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, redirect, get_object_or_404

from django.contrib.auth import views
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
# Create your views here.
from ticket.forms import TicketForm, CardForm
from ticket.models import Card, Fee


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

        pass

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
        'page_range': page_range,
        'count': count,
        'page_nums': page_nums,
        'page_title': '基础资料',
        'sub_title': sub_title,
    }
    #与res_add.html用同一个页面，只是edit会在res_add页面做数据填充
    return render(request, 'ticket/card_edit.html', context)

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
