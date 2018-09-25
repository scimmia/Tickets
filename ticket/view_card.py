from django.shortcuts import get_object_or_404, redirect, render

from ticket import utils
from ticket.forms import CardForm, CardTransForm
from ticket.models import Card, CardTrans, FeeDetail
from ticket.utils import LogTemp


def card_list(request):
    form = CardForm(request.POST or None)
    context = {
        'form': form,
    }
    if request.method == 'POST':
        instance = form.save()
        log = LogTemp()
        log.oper_type = 401
        log.add_detail_card(instance.pk)
        log.save()
        context['message'] = u'保存成功'
    raw_data = Card.objects.all()
    list_template = 'ticket/card_list.html'
    return utils.get_paged_page(request, raw_data, list_template,context)


# 修改数据,函数中的pk代表数据的id
def card_edit(request, pk):
    card_ins = get_object_or_404(Card, pk=pk)
    context = {
        'item': card_ins,
    }
    if request.method == 'POST':
        card_ins.name = request.POST['name']
        card_ins.beizhu = request.POST['beizhu']
        card_ins.card_type = request.POST['card_type']
        card_ins.save()

        if request.POST['fee'].strip(' ') != '':
            log = LogTemp()
            log.oper_type = 402
            money = float(request.POST['fee'])
            if request.POST['p_status'] == '4':  # 银行卡取出
                money = 0 - money
                log.oper_type = 403
            log.add_detail_card(pk)
            log.add_xianjin(money)
            log.save()
            utils.create_card_fee(card_ins, money, log)
        context['message'] = u'保存成功'

    fee_data = FeeDetail.objects.filter(fee_detail_type=5,fee_detail_pk=pk).order_by('-pub_date')
    return utils.get_paged_page(request, fee_data, 'ticket/card_edit.html', context)


# 修改数据,函数中的pk代表数据的id
def card_trans(request):
    form = CardTransForm(request.POST or None)
    context = {
        'form': form
    }
    if request.method == 'POST':
        if form.is_valid():
            instance = form.save(commit=False)
            if instance.fromCard == instance.toCard:
                context['message'] = u'请选择不同的银行卡'
            elif instance.money <= 0:
                context['message'] = u'转账金额不能小于0'
            else:
                instance.save()
                log = LogTemp()
                log.oper_type = 404
                log.add_detail_card(instance.fromCard.pk)
                log.add_detail_card(instance.fromCard.pk)
                log.save()
                utils.create_card_fee(instance.fromCard, 0 - instance.money, log)
                utils.create_card_fee(instance.toCard, instance.money, log)
                context['message'] = u'转账成功'

    data = CardTrans.objects.all().order_by('-pub_date')
    return utils.get_paged_page(request, data, 'ticket/card_trans.html', context)
