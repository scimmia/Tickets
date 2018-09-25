import json
import os

from django.http import FileResponse
from django.shortcuts import render

from ticket import utils
from ticket.forms import BestMixForm
from ticket.models import InpoolPercent, InpoolPercentDetail, OperLog


class MixItem(object):
    def __init__(self, form, key):
        value = form.cleaned_data.get(('value%s' % key))
        tiexi = form.cleaned_data.get(('valuet%s' % key))
        group = int(form.cleaned_data.get(('group%s' % key)))
        if value is None:
            value = 0
            tiexi = 0
        self.title = value
        self.value = value
        self.tiexi = tiexi
        self.group = group


class GroupItems(object):
    def __init__(self):
        self.d = {1: {'total': 0, 'count': 0},
                  2: {'total': 0, 'count': 0},
                  3: {'total': 0, 'count': 0},
                  4: {'total': 0, 'count': 0},
                  5: {'total': 0, 'count': 0}}

    def addItem(self, item):
        if item.value > 0 and item.group in self.d:
            self.d[item.group]['count'] += 1
            self.d[item.group]['total'] += item.value
            pass


def best_mix(request):
    form = BestMixForm(request.POST or None)
    items = []
    keys = []
    values = []
    # d = {'1': [], '2': [], '3': [], '4': [], '5': []}
    groupItem = GroupItems()
    if request.method == 'POST':
        if form.is_valid():
            money_sum = form.cleaned_data.get('money')
            count = form.cleaned_data.get('count')
            changecount = form.cleaned_data.get('changecount')
            items.append(MixItem(form, 'a'))
            items.append(MixItem(form, 'b'))
            items.append(MixItem(form, 'c'))
            items.append(MixItem(form, 'd'))
            items.append(MixItem(form, 'e'))
            keys.append('总张数')
            for item in items:
                groupItem.addItem(item)
                keys.append(item.title)
            keys.append('总和')
            if changecount is None:
                changecount = 0
            step = 1
            start = min(count, count + changecount)
            end = max(count, count + changecount)
            while start <= end:
                maxa = 0
                maxb = 0
                maxc = 0
                maxd = 0
                maxe = 0
                if groupItem.d[1]['count'] > 0:
                    maxa = min(money_sum / groupItem.d[1]['total'], start / groupItem.d[1]['count'])
                if groupItem.d[2]['count'] > 0:
                    maxb = min(money_sum / groupItem.d[2]['total'], start / groupItem.d[2]['count'])
                if groupItem.d[3]['count'] > 0:
                    maxc = min(money_sum / groupItem.d[3]['total'], start / groupItem.d[3]['count'])
                if groupItem.d[4]['count'] > 0:
                    maxd = min(money_sum / groupItem.d[4]['total'], start / groupItem.d[4]['count'])
                if groupItem.d[5]['count'] > 0:
                    maxe = min(money_sum / groupItem.d[5]['total'], start / groupItem.d[5]['count'])
                a = 0
                while a <= maxa:
                    b = 0
                    while b <= min(maxb, start - a):
                        c = 0
                        while c <= min(maxc, start - a - b):
                            d = 0
                            while d <= min(maxd, start - a - b - c):
                                e = 0
                                while e <= min(maxe, start - a - b - c - d):
                                    if (a * groupItem.d[1]['count'] + b * groupItem.d[2]['count']
                                            + c * groupItem.d[3]['count'] + d * groupItem.d[4]['count'] + e *
                                            groupItem.d[5]['count'] == start
                                            and a * groupItem.d[1]['total'] + b * groupItem.d[2]['total']
                                            + c * groupItem.d[3]['total'] + d * groupItem.d[4]['total'] + e *
                                            groupItem.d[5]['total'] == money_sum):
                                        sum_temp = 0
                                        a_t = b_t = c_t = d_t = e_t = 0
                                        value = []
                                        value.append(start)
                                        for item in items:
                                            if item.group == 1:
                                                sum_temp += a * item.value * item.tiexi
                                                value.append(a)
                                            elif item.group == 2:
                                                sum_temp += b * item.value * item.tiexi
                                                value.append(b)
                                            elif item.group == 3:
                                                sum_temp += c * item.value * item.tiexi
                                                value.append(c)
                                            elif item.group == 4:
                                                sum_temp += d * item.value * item.tiexi
                                                value.append(d)
                                            elif item.group == 5:
                                                sum_temp += e * item.value * item.tiexi
                                                value.append(e)
                                        value.append(sum_temp)
                                        values.append(value)
                                    e += 1
                                d = d + 1
                            c += 1
                        b = b + 1
                    a = a + 1
                start = start + step
            pass
    return render(request, 'ticket/tool_bestmix.html', locals())


def avg_day(request):
    return render(request, 'ticket/tool_avgday.html')


def tiexian(request):
    return render(request, 'ticket/tool_tiexian.html')


def create_pool_percent(tag, inpoolPer):
    try:
        obj, created = InpoolPercent.objects.update_or_create(
            tags=tag,
            defaults={'inpoolPer': inpoolPer},
        )
        temp = InpoolPercentDetail()
        temp.inpoolPercent = obj
        temp.inpoolPer = inpoolPer
        temp.save()
        return True
    except:
        return False


def pool_percent_list(request):
    if InpoolPercent.objects.filter(tags='!默认!').count() == 0:
        create_pool_percent('!默认!', 100)
    if request.method == 'POST':
        tag = request.POST['thetags']
        inpoolPer = request.POST['inpoolPer']
        if create_pool_percent(tag, inpoolPer):
            message = u'保存成功'
        else:
            message = u'保存失败'

    data = InpoolPercent.objects.all().order_by('tags')

    return render(request, 'ticket/inpoolPer_list.html', locals())


def pool_percent_detail(request):
    if 'tag' in request.GET.keys():
        tag = request.GET['tag']

    if request.method == 'POST':
        inpoolPer = request.POST['inpoolPer']
        if create_pool_percent(tag, inpoolPer):
            message = u'保存成功'
        else:
            message = u'保存失败'
    data = InpoolPercentDetail.objects.filter(inpoolPercent__tags=tag).order_by('-pub_date')
    items_total = []
    items_date = []
    for i in range(len(data)):
        list.insert(items_total, 0, data[i].inpoolPer)
        list.insert(items_date, 0, data[i].pub_date)
    item = data[0]
    return render(request, 'ticket/inpoolPer.html', locals())


# 日志
def log_list(request):
    raw_data = OperLog.objects.all().order_by('-pub_date')
    kwargs, query = utils.get_query(request)

    data = raw_data.filter(**kwargs)
    data_list, page_range, count, page_nums = utils.pagination(request, data)

    for t in data_list:
        try:
            t.detail = json.loads(t.detail)
            t.contdetail = json.loads(t.contdetail)
        except:
            pass
    # 建立context字典，将值传递到相应页面
    context = {
        'data': data_list,
        'query': query,
        'page_range': page_range,
        'count': count,
        'page_nums': page_nums,
        'filter': filter,
    }
    return render(request, 'ticket/log_list.html', context)


# todo
def daily_report(request):
    if request.method == "POST":
        if 'day' in request.POST.keys():
            day = request.POST['day']
            print(day)
            filename = day + '.xlsx'
            fullpath = 'static/dailyreport/' + filename
            if os.path.exists(fullpath):
                file = open(fullpath, 'rb')
                response = FileResponse(file)
                response['Content-Type'] = 'application/octet-stream'
                response['Content-Disposition'] = 'attachment;filename="%s"' % (filename)
                return response
            else:
                message = u'文件不存在'
    if request.method == 'GET':
        if 'day' in request.GET.keys():
            filename = request.GET['day']
            fullpath = 'static/dailyreport/' + filename
            if os.path.exists(fullpath):
                file = open(fullpath, 'rb')
                response = FileResponse(file)
                response['Content-Type'] = 'application/octet-stream'
                response['Content-Disposition'] = 'attachment;filename="%s"' % (filename)
                return response
            else:
                message = u'文件不存在'
        pass
    files = os.listdir('static/dailyreport')
    return render(request, 'ticket/dailyreport.html', locals())
