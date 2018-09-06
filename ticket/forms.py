# -*- coding: UTF-8 -*-
from django.forms import ModelForm
from django import forms

from ticket.models import Ticket, Card, Pool, Fee, Loan_Order, CardTrans, SuperLoan


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
    fee_status = forms.ChoiceField(label="额外费用类型",required=False,
        choices=(
            (1, "收入"),
            (2, "支出"),
        ),
        widget=forms.Select,
        initial='2',
    )
    #自定义ModelForm的内容
    class Meta:
        #该ModelForm参照Model: Node
        model = Fee

        fields = ['yinhangka','name','money',]
class CardForm(ModelForm):
    #自定义ModelForm的内容
    class Meta:
        #该ModelForm参照Model: Node
        model = Card
        #在Form中不显示node_signer这个字段
        exclude = ['money']
class CardTransForm(ModelForm):
    class Meta:
        model = CardTrans
        exclude = ['pub_date']

class PoolForm(ModelForm):
    #自定义ModelForm的内容
    p_status = forms.ChoiceField(label="类型",
        choices=(
            (3, "存入"),
            (4, "取出"),
        ),
        widget=forms.Select,
        initial='1',
    )
    class Meta:
        #该ModelForm参照Model: Node
        model = Pool
        #在Form中不显示node_signer这个字段
        fields = ['p_status','money','card',]

class SuperLoanForm(ModelForm):
    isMonthlilv = forms.BooleanField(label="是否月利率",required=False,)
    class Meta:
        model = SuperLoan
        fields = ['benjin','isMonthlilv','lilv','lixi_begin_date',]

class SuperLoanFeeForm(forms.Form):
    money = forms.FloatField(label="金额",required=True, widget=forms.NumberInput(attrs={'class': 'form-control'}))

class LoanForm(ModelForm):
    isMonthlilv = forms.BooleanField(label="是否月利率",required=False,)

    class Meta:
        #该ModelForm参照Model: Node
        model = Loan_Order
        fields = ['jiedairen','benjin','isMonthlilv','lilv','lixi_begin_date','yinhangka',]

class BestMixForm(forms.Form):
    money = forms.IntegerField(label="总金额",required=True, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    count = forms.IntegerField(label="总张数",required=True, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    changecount = forms.IntegerField(label="浮动张数",required=False,widget=forms.NumberInput(attrs={'class': 'form-control'}))
    valuea = forms.IntegerField(label="票面价格1",required=True, min_value=1,widget=forms.NumberInput(attrs={'class': 'form-control'}))
    valueta = forms.IntegerField(label="每十万贴息1",required=True, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    valueb = forms.IntegerField(label="票面价格2",required=True, min_value=1,widget=forms.NumberInput(attrs={'class': 'form-control'}))
    valuetb = forms.IntegerField(label="每十万贴息2",required=True, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    valuec = forms.IntegerField(label="票面价格3",required=True, min_value=1,widget=forms.NumberInput(attrs={'class': 'form-control'}))
    valuetc = forms.IntegerField(label="每十万贴息3",required=True, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    valued = forms.IntegerField(label="票面价格4",required=False, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    valuetd = forms.IntegerField(label="每十万贴息4",required=False, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    valuee = forms.IntegerField(label="票面价格5",required=False, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    valuete = forms.IntegerField(label="每十万贴息5",required=False, widget=forms.NumberInput(attrs={'class': 'form-control'}))
