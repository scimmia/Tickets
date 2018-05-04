# -*- coding: UTF-8 -*-
from django.forms import ModelForm
from django import forms

from ticket.models import Ticket, Card


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
        exclude = []
class TicketEditForm(ModelForm):

    #自定义ModelForm的内容
    class Meta:
        #该ModelForm参照Model: Node
        model = Ticket

        #在Form中不显示node_signer这个字段
        exclude = []


class CardForm(ModelForm):
    #自定义ModelForm的内容
    class Meta:
        #该ModelForm参照Model: Node
        model = Card
        #在Form中不显示node_signer这个字段
        exclude = ['money']


class PoolForm(ModelForm):
    #自定义ModelForm的内容
    class Meta:
        #该ModelForm参照Model: Node
        model = Card
        #在Form中不显示node_signer这个字段
        fields = []