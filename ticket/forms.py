# -*- coding: UTF-8 -*-
from django.forms import ModelForm
from django import forms

from ticket.models import Ticket, Card, Pool, Fee, Loan_Order, CardTrans, SuperLoan, Per_Detail, MoneyWithCard, \
    PoolLicai


class TicketForm(ModelForm):

    fenshu = forms.IntegerField(label="份数",required=False, widget=forms.NumberInput(attrs={'class': 'form-control'}))

    #自定义ModelForm的内容
    class Meta:
        #该ModelForm参照Model: Node
        model = Ticket
        #在Form中不显示node_signer这个字段
        exclude = ['gouruhuilv','pay_status','maichulilv','maichujiage','sell_status','lirun',]
class TicketEditForm(ModelForm):

    #自定义ModelForm的内容
    class Meta:
        #该ModelForm参照Model: Node
        model = Ticket

        #在Form中不显示node_signer这个字段
        exclude = []
class TicketFeeForm(ModelForm):

    #自定义ModelForm的内容
    class Meta:
        #该ModelForm参照Model: Node
        model = Fee

        #在Form中不显示node_signer这个字段
        fields = ['yinhangka','name','money',]
class TicketOrderFeeForm(ModelForm):
    class Meta:
        #该ModelForm参照Model: Node
        model = Fee

        fields = ['yinhangka','name','money',]
class MoneyWithCardForm(ModelForm):
    class Meta:
        model = MoneyWithCard
        fields = ['card','money',]
class CardForm(ModelForm):
    class Meta:
        model = Card
        exclude = ['money']
class CardTransForm(ModelForm):
    class Meta:
        model = CardTrans
        exclude = ['pub_date']

class PoolForm(ModelForm):
    p_status = forms.ChoiceField(label="类型",
        choices=(
            (3, "存入"),
            (4, "取出"),
        ),
        widget=forms.RadioSelect,
        initial='3',
    )
    class Meta:
        model = MoneyWithCard
        fields = ['p_status','money','card',]


class ProForm(ModelForm):
    p_status = forms.ChoiceField(label="类型",
        choices=(
            (1, "存入"),
            (2, "取出"),
        ),
        widget=forms.RadioSelect,
        initial='1',
    )
    class Meta:
        model = MoneyWithCard
        fields = ['p_status','money','card',]

class SuperLoanForm(ModelForm):
    isMonthlilv = forms.ChoiceField(label="",
        choices=(
            (3, "月利率（‰）"),
            (4, "年利率（%）"),
        ),
        widget=forms.RadioSelect,
        initial='3',
    )
    class Meta:
        model = SuperLoan
        fields = ['benjin','isMonthlilv','lilv','lixi_begin_date','lixi_end_date']

class PoolLicaiForm(ModelForm):
    isMonthlilv = forms.ChoiceField(label="",
        choices=(
            (1, "年利率（%）"),
            (2, "月利率（‰）"),
        ),
        widget=forms.RadioSelect,
        initial='1',
    )
    class Meta:
        model = PoolLicai
        fields = ['benjin','isMonthlilv','lilv','lixi_begin_date','lixi_end_date','is_front','yinhangka']

class SuperLoanFeeForm(forms.Form):
    money = forms.FloatField(label="金额",required=True, widget=forms.NumberInput(attrs={'class': 'form-control'}))

class LoanForm(ModelForm):

    isMonthlilv = forms.ChoiceField(label="",
        choices=(
            (1, "年利率（%）"),
            (2, "月利率（‰）"),
        ),
        widget=forms.RadioSelect,
        initial='1',
    )
    class Meta:
        model = Loan_Order
        fields = ['benjin','isMonthlilv','lilv','lixi_begin_date','lixi_end_date','yinhangka',]

class LoanPreForm(ModelForm):
    class Meta:
        model = Per_Detail
        fields = ['money','yinhangka',]

class BestMixForm(forms.Form):
    choices = (
        (1, "1"),
        (2, "2"),
        (3, "3"),
        (4, "4"),
        (5, "5"),
    )
    money = forms.IntegerField(label="总金额",required=True, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    count = forms.IntegerField(label="总张数",required=True, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    changecount = forms.IntegerField(label="浮动张数",required=False,widget=forms.NumberInput(attrs={'class': 'form-control'}))

    groupa = forms.ChoiceField(label="分组1",
                                     choices=choices,
                                     widget=forms.Select,
                                     initial='1',
                                     )
    groupb = forms.ChoiceField(label="分组2",
                                     choices=choices,
                                     widget=forms.Select,
                                     initial='2',
                                     )
    groupc = forms.ChoiceField(label="分组3",
                                     choices=choices,
                                     widget=forms.Select,
                                     initial='3',
                                     )
    groupd = forms.ChoiceField(label="分组4",
                                     choices=choices,
                                     widget=forms.Select,
                                     initial='4',
                                     )
    groupe = forms.ChoiceField(label="分组5",
                                     choices=choices,
                                     widget=forms.Select,
                                     initial='5',
                                     )
    valuea = forms.IntegerField(label="票面价格1",required=True, min_value=1,widget=forms.NumberInput(attrs={'class': 'form-control'}))
    valueta = forms.IntegerField(label="每十万贴息1",required=True, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    valueb = forms.IntegerField(label="票面价格2",required=True, min_value=1,widget=forms.NumberInput(attrs={'class': 'form-control'}))
    valuetb = forms.IntegerField(label="每十万贴息2",required=True, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    valuec = forms.IntegerField(label="票面价格3",required=False, min_value=1,widget=forms.NumberInput(attrs={'class': 'form-control'}))
    valuetc = forms.IntegerField(label="每十万贴息3",required=False, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    valued = forms.IntegerField(label="票面价格4",required=False, min_value=1,widget=forms.NumberInput(attrs={'class': 'form-control'}))
    valuetd = forms.IntegerField(label="每十万贴息4",required=False, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    valuee = forms.IntegerField(label="票面价格5",required=False,min_value=1, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    valuete = forms.IntegerField(label="每十万贴息5",required=False, widget=forms.NumberInput(attrs={'class': 'form-control'}))
