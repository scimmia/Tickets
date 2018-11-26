from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404

from ticket import utils
from ticket.forms import CardForm, CardTransForm, CardfeeForm
from ticket.models import Card, CardTrans, FeeDetail


@login_required
def card_list(request):
    form = CardForm(request.POST or None)
    context = {
        'form': form,
    }
    if request.method == 'POST':
        instance = form.save()
        log, detail = utils.create_log(request.user.last_name)
        log.oper_type = 401
        detail.add_detail_card(instance.pk)
        utils.save_log(log, detail)
        context['message'] = u'保存成功'
    raw_data = Card.objects.all()
    list_template = 'ticket/card_list.html'
    return utils.get_paged_page(request, raw_data, list_template,context)


# 修改数据,函数中的pk代表数据的id
@login_required
def card_edit(request, pk):
    card_ins = get_object_or_404(Card, pk=pk)
    form = CardForm(request.POST or None, instance=card_ins)
    feeform = CardfeeForm(request.POST or None)
    context = {
        'item': card_ins,
    }
    if request.method == 'POST':
        if form.is_valid():
            feeform = CardfeeForm()
            form.save()
            context['message'] = u'编辑成功'
        elif feeform.is_valid():

            log, detail = utils.create_log(request.user.last_name)
            log.oper_type = 402
            money = feeform.cleaned_data.get('fee_money')
            if feeform.cleaned_data.get('fee_status') == '2':  # 银行卡取出
                money = 0 - money
                log.oper_type = 403
            detail.add_detail_card(pk)
            utils.create_card_fee(card_ins, money, log, feeform.cleaned_data.get('fee_beizhu'))
            utils.save_log(log, detail)
            form = CardForm(instance=card_ins)
            context['message'] = u'保存成功'
    context['form'] = form
    context['feeform'] = feeform
    fee_data = FeeDetail.objects.filter(fee_detail_type=5,fee_detail_pk=pk).order_by('-pub_date')
    return utils.get_paged_page(request, fee_data, 'ticket/card_edit.html', context)


# 修改数据,函数中的pk代表数据的id
@login_required
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
                log,detail = utils.create_log(request.user.last_name)
                log.oper_type = 404
                detail.add_detail_card(instance.fromCard.pk)
                utils.create_card_fee(instance.fromCard, 0 - instance.money, log)
                detail.add_detail_card(instance.toCard.pk)
                utils.create_card_fee(instance.toCard, instance.money, log)
                utils.save_log(log,detail)
                context['message'] = u'转账成功'

    data = CardTrans.objects.all().order_by('-pub_date')
    return utils.get_paged_page(request, data, 'ticket/card_trans.html', context)
