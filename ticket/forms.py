# -*- coding: UTF-8 -*-
from django.forms import ModelForm
from django import forms

from ticket.models import Ticket, Card, Pool, Fee, Loan_Order


class TicketForm(ModelForm):

    fenshu = forms.IntegerField(label="份数",required=False, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    # maichuriqi = forms.DateTimeField(label="卖出日期", editable=False)
    # def clean(self):
    #     if (not self.cleaned_data.get('gouruzijinchi')) and (not self.cleaned_data.get('gourucard')):
    #         raise forms.ValidationError(u"两次密码必须一致")
    #     self._validate_unique = True
    #     return self.cleaned_data

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
    isOrderFee = forms.BooleanField(label="是否额外费用",required=False,)
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

class SuperLoanForm(forms.Form):
    money = forms.FloatField(label="金额",required=True, widget=forms.NumberInput(attrs={'class': 'form-control'}))

class LoanForm(ModelForm):
    isMonthlilv = forms.BooleanField(label="是否月利率",required=False,)

    class Meta:
        #该ModelForm参照Model: Node
        model = Loan_Order
        fields = ['jiedairen','money_benjin','isMonthlilv','money_lilv','order_date','yinhangka',]