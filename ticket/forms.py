# -*- coding: UTF-8 -*-
from django.forms import ModelForm
from django import forms

from ticket.models import Ticket, Card, Pool, Fee


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
        exclude = ['ticket','order','fee_type','pub_date',]
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

        #在Form中不显示node_signer这个字段
        exclude = ['ticket','order','fee_type','pub_date',]
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

    # def __init__(self, *args, **kwargs):
    #     # first call parent's constructor
    #     super(PoolForm, self).__init__(*args, **kwargs)
    #     # there's a `fields` property now
    #     self.fields['card'].required = True
    class Meta:
        #该ModelForm参照Model: Node
        model = Pool
        #在Form中不显示node_signer这个字段
        fields = ['p_status','money','card',]