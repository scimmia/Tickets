# -*- coding: UTF-8 -*-
from django.forms import ModelForm
from django import forms

from ticket.models import Ticket, Card, Loan_Order, CardTrans, SuperLoan, Per_Detail, MoneyWithCard, \
    PoolLicai, MoneyWithCardPool, PoolPercent, Pool, Ticket_Import


class TicketForm(ModelForm):
    fenshu = forms.IntegerField(label="份数", required=False, widget=forms.NumberInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Ticket
        exclude = ['gouruhuilv', 'pay_status', 'maichulilv', 'maichujiage', 'sell_status', 'lirun', ]


class TicketEditForm(ModelForm):
    class Meta:
        model = Ticket
        exclude = []


class TicketTransForm(forms.Form):
    p_status = forms.ChoiceField(label="",
                                 choices=(
                                     (1, "入库"),
                                     (2, "入池"),
                                 ),
                                 widget=forms.RadioSelect,
                                 initial='1',
                                 )
    pool = forms.ModelChoiceField(label=" ", queryset=Pool.objects.all(), required=False)


class TicketImportForm(ModelForm):
    class Meta:
        model = Ticket_Import
        fields = ['import_type', 'pool', ]


class MoneyWithCardForm(ModelForm):
    beizhu = forms.CharField(label="备注", required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = MoneyWithCard
        fields = ['card', 'money']


class CardForm(ModelForm):
    class Meta:
        model = Card
        exclude = ['money']


class CardfeeForm(forms.Form):
    fee_status = forms.ChoiceField(label="类型",
                                 choices=(
                                     (1, "存入"),
                                     (2, "取出"),
                                 ),
                                 widget=forms.RadioSelect,
                                 initial='1',
                                 )
    fee_money = forms.DecimalField(label="金额", required=True, decimal_places=2)
    fee_beizhu = forms.CharField(label="备注", required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))


class CardTransForm(ModelForm):
    class Meta:
        model = CardTrans
        exclude = ['pub_date']


class PoolForm(ModelForm):
    class Meta:
        model = Pool
        fields = ['name', 'yinhangka']


class PoolPercentForm(ModelForm):
    class Meta:
        model = PoolPercent
        fields = ['pool', 'tags', 'inpoolPer']


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
        model = MoneyWithCardPool
        fields = ['pool', 'p_status', 'money', ]


class SuperLoanForm(ModelForm):
    super_isMonthlilv = forms.ChoiceField(label="",
                                    choices=(
                                        (1, "年利率（%）"),
                                        (2, "月利率（‰）"),
                                    ),
                                    widget=forms.RadioSelect,
                                    initial='1',
                                    )
    class Meta:
        model = SuperLoan
        fields = ['pool', 'benjin', 'super_isMonthlilv', 'lilv', 'lixi_begin_date', 'lixi_end_date']


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
        fields = ['pool', 'benjin', 'isMonthlilv', 'lilv', 'lixi_begin_date', 'lixi_end_date', 'is_front', 'beizhu']


class MoneyForm(forms.Form):
    money = forms.DecimalField(label="金额", required=True, decimal_places=2)


class MoneyBeizhuForm(forms.Form):
    money = forms.DecimalField(label="金额", required=True, decimal_places=2)
    beizhu = forms.CharField(label="备注", required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))


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
        fields = ['benjin', 'isMonthlilv', 'lilv', 'lixi_begin_date', 'lixi_end_date', 'yinhangka', ]


class LoanPreForm(ModelForm):
    class Meta:
        model = Per_Detail
        fields = ['money', 'yinhangka', ]


class BestMixForm(forms.Form):
    choices = (
        (1, "1"),
        (2, "2"),
        (3, "3"),
        (4, "4"),
        (5, "5"),
    )
    money = forms.IntegerField(label="总金额", required=True, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    count = forms.IntegerField(label="总张数", required=True, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    changecount = forms.IntegerField(label="浮动张数", required=False,
                                     widget=forms.NumberInput(attrs={'class': 'form-control'}))

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
    valuea = forms.IntegerField(label="票面价格1", required=True, min_value=1,
                                widget=forms.NumberInput(attrs={'class': 'form-control'}))
    valueta = forms.IntegerField(label="每十万贴息1", required=True,
                                 widget=forms.NumberInput(attrs={'class': 'form-control'}))
    valueb = forms.IntegerField(label="票面价格2", required=True, min_value=1,
                                widget=forms.NumberInput(attrs={'class': 'form-control'}))
    valuetb = forms.IntegerField(label="每十万贴息2", required=True,
                                 widget=forms.NumberInput(attrs={'class': 'form-control'}))
    valuec = forms.IntegerField(label="票面价格3", required=False, min_value=1,
                                widget=forms.NumberInput(attrs={'class': 'form-control'}))
    valuetc = forms.IntegerField(label="每十万贴息3", required=False,
                                 widget=forms.NumberInput(attrs={'class': 'form-control'}))
    valued = forms.IntegerField(label="票面价格4", required=False, min_value=1,
                                widget=forms.NumberInput(attrs={'class': 'form-control'}))
    valuetd = forms.IntegerField(label="每十万贴息4", required=False,
                                 widget=forms.NumberInput(attrs={'class': 'form-control'}))
    valuee = forms.IntegerField(label="票面价格5", required=False, min_value=1,
                                widget=forms.NumberInput(attrs={'class': 'form-control'}))
    valuete = forms.IntegerField(label="每十万贴息5", required=False,
                                 widget=forms.NumberInput(attrs={'class': 'form-control'}))


class UserCreatForm(forms.Form):
    username = forms.CharField(label="姓名", required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    loginname = forms.CharField(label="账号", required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))


class UserManageForm(forms.Form):
    operation = forms.ChoiceField(label="操作类型",
                                  choices=(
                                      (1, "重置密码"),
                                      (2, "启用"),
                                      (3, "停用"),
                                  ),
                                  widget=forms.RadioSelect,
                                  initial='1',
                                  )


class UserChangePasswordForm(forms.Form):
    old_password = forms.CharField(label="旧密码", required=True, widget=forms.PasswordInput(attrs={'autofocus': True}), )
    new_password = forms.CharField(label="新密码", required=True, widget=forms.PasswordInput(), )
    new_password_2 = forms.CharField(label="新密码确认", required=True, widget=forms.PasswordInput(), )
