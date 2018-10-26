import json
import os

from django.contrib.auth.decorators import login_required
from django.http import FileResponse
from django.shortcuts import render

from ticket import utils
from ticket.forms import BestMixForm
from ticket.models import OperLog


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




# 日志
@login_required
def log_list(request):
    raw_data = OperLog.objects.all().order_by('-pub_date')
    kwargs, query = utils.get_query(request)

    data = raw_data.filter(**kwargs)
    data_list, page_range, count, page_nums = utils.pagination(request, data)

    for t in data_list:
        try:
            t.detail = json.loads(t.detail)
            t.username = t.contdetail
            t.contdetail = []
            if t.xianjin != 0:
                t.contdetail.append({'cont': u'银行卡', 'money': t.xianjin})
            if t.kucun != 0:
                t.contdetail.append({'cont': u'库存', 'money': t.kucun})
            if t.edu_keyong != 0:
                t.contdetail.append({'cont': u'可用额度', 'money': t.edu_keyong})
            if t.edu_yiyong != 0:
                t.contdetail.append({'cont': u'已用额度', 'money': t.edu_yiyong})
            if t.edu_baozhengjin != 0:
                t.contdetail.append({'cont': u'保证金', 'money': t.edu_baozhengjin})
            if t.edu_chineipiao != 0:
                t.contdetail.append({'cont': u'池内票', 'money': t.edu_chineipiao})
            if t.edu_licai != 0:
                t.contdetail.append({'cont': u'理财', 'money': t.edu_licai})
            if t.edu_chaoduandai != 0:
                t.contdetail.append({'cont': u'超短贷', 'money': t.edu_chaoduandai})
            if t.need_collect != 0:
                t.contdetail.append({'cont': u'应收', 'money': t.need_collect})
            if t.need_pay != 0:
                t.contdetail.append({'cont': u'应付', 'money': t.need_pay})
            if t.yushou != 0:
                t.contdetail.append({'cont': u'预收', 'money': t.yushou})
            if t.yufu != 0:
                t.contdetail.append({'cont': u'预付', 'money': t.yufu})
            if t.feiyong_yewu != 0:
                t.contdetail.append({'cont': u'业务费用', 'money': t.feiyong_yewu})
            if t.feiyong_ziben != 0:
                t.contdetail.append({'cont': u'资本费用', 'money': t.feiyong_ziben})
            if t.feiyong_za != 0:
                t.contdetail.append({'cont': u'管理杂费', 'money': t.feiyong_za})
            if t.lirun_yewu != 0:
                t.contdetail.append({'cont': u'业务利润', 'money': t.lirun_yewu})
            if t.lirun_ziben != 0:
                t.contdetail.append({'cont': u'资本收益', 'money': t.lirun_ziben})
            if t.lirun_za != 0:
                t.contdetail.append({'cont': u'其他利润', 'money': t.lirun_za})
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


@login_required
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
