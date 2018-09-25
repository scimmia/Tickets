from django.conf.urls import url

from ticket import view_tools, view_card, view_pool, view_loan, view_tickets
from . import views

urlpatterns = [
    url(r'^dashboard/', views.dashboard, name='dashboard'),

    # 用户登陆列表
    # 用户登陆
    url(r'login/', views.login, name='login'),
    # 用户退出
    url(r'logout/', views.logout, name='logout'),
    # 密码修改
    url(r'password_change/', views.password_change, name='password_change'),

    # 任务列表
    url(r'^ticket/ticket_list/', view_tickets.ticket_list, name='ticket_list'),
    url(r'^ticket/tickets_needfix/', views.tickets_needfix, name='tickets_needfix'),
    url(r'^ticket/ticket_needpay/', views.ticket_needpay, name='ticket_needpay'),
    url(r'^ticket/ticket_needcollect/', views.ticket_needcollect, name='ticket_needcollect'),
    url(r'^ticket/ticket_createorder/', views.ticket_createorder, name='ticket_createorder'),
    # url(r'^ticket/ticket_createorder/', views.ticket_createorder, name='ticket_createorder'),
    url(r'^order/ticket_payorders/', views.ticket_payorders, name='ticket_payorders'),
    url(r'^order/ticket_payorder/(?P<pk>\d+)/$', views.ticket_payorder, name='ticket_payorder'),
    url(r'^order/ticket_sellorders/', views.ticket_sellorders, name='ticket_sellorders'),
    url(r'^order/ticket_sellorder/(?P<pk>\d+)/$', views.ticket_sellorder, name='ticket_sellorder'),
    url(r'^ticket/ticket_add/', view_tickets.ticket_add, name='ticket_add'),
    url(r'^ticket/ticket_import', views.ticket_import, name='ticket_import'),
    url(r'^ticket/flow_import', views.flow_import, name='flow_import'),
    url(r'^ticket/pool_import', views.pool_import, name='pool_import'),
    url(r'^ticket/ticket_index/(?P<pk>\d+)/$', views.ticket_index, name='ticket_index'),
    url(r'^ticket/ticket_fix/', views.ticket_fix, name='ticket_fix'),
    # url(r'^ticket_delete/(?P<pk>\d+)/$', views.ticket_delete, name='ticket_delete'),
    # url(r'^ticket_finish/(?P<pk>\d+)/$', views.ticket_finish, name='ticket_finish'),
    url(r'^loan/borrow_status/', views.borrow_status, name='borrow_status'),
    url(r'^loan/loan_status/', views.loan_status, name='loan_status'),
    url(r'^loan/pre_collect/', views.pre_collect, name='pre_collect'),
    url(r'^loan/pre_pay/', views.pre_pay, name='pre_pay'),
    url(r'^loan/borrow_list/(?P<pk>\d+)/$', views.borrow_list, name='borrow_list'),
    url(r'^loan/loan_list/(?P<pk>\d+)/$', views.loan_list, name='loan_list'),
    url(r'^loan/pre_collect_list/(?P<pk>\d+)/$', views.pre_collect_list, name='pre_collect_list'),
    url(r'^loan/pre_pay_list/(?P<pk>\d+)/$', views.pre_pay_list, name='pre_pay_list'),
    url(r'^loan/order/(?P<pk>\d+)/$', view_loan.loanorder, name='loanorder'),

    url(r'^loan/need_collect_customers/', view_loan.need_collect_customers, name='need_collect_customers'),
    url(r'^loan/need_pay_customers/', view_loan.need_pay_customers, name='need_pay_customers'),
    url(r'^loan/pre_collect_customers/', view_loan.pre_collect_customers, name='pre_collect_customers'),
    url(r'^loan/pre_pay_customers/', view_loan.pre_pay_customers, name='pre_pay_customers'),
    url(r'^loan/need_collect_lists/(?P<pk>\d+)/$', view_loan.need_collect_lists, name='need_collect_lists'),
    url(r'^loan/need_pay_lists/(?P<pk>\d+)/$', view_loan.need_pay_lists, name='need_pay_lists'),

    url(r'^pool/pool_dash/', view_pool.pool_dash, name='pool_dash'),
    url(r'^pool/pool_licai_lists/', view_pool.pool_licai_lists, name='pool_licai_lists'),
    url(r'^pool/super_loan_lists/', view_pool.super_loan_lists, name='super_loan_lists'),
    url(r'^pool/super_loan/(?P<pk>\d+)/$', view_pool.super_loan, name='pool_loan'),
    url(r'^pool/pool_loan_repay/', views.pool_loan_repay, name='pool_loan_repay'),
    url(r'^pool/pool_tickets/', view_pool.pool_tickets, name='pool_tickets'),

    url(r'^card/card_list/', view_card.card_list, name='card_list'),
    url(r'^card/card_edit/(?P<pk>\d+)/$', view_card.card_edit, name='card_edit'),
    url(r'^card/card_trans/', view_card.card_trans, name='card_trans'),

    url(r'^log/log_list/', view_tools.log_list, name='log_list'),
    url(r'^download/dailyreport/', view_tools.daily_report, name='dailyreport'),

    url(r'^tool/bestmix/', view_tools.best_mix, name='bestmix'),
    url(r'^tool/avgday/', view_tools.avg_day, name='avgday'),
    url(r'^tool/tiexian/', view_tools.tiexian, name='tiexian'),

    url(r'^sysconfig/inpoolPercent_list', view_tools.pool_percent_list, name='inpoolPercentList'),
    url(r'^sysconfig/inpoolPercent_detail', view_tools.pool_percent_detail, name='inpoolPercentDetail'),

]