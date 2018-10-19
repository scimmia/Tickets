from django.conf.urls import url

from ticket import view_tools, view_card, view_pool, view_loan, view_tickets
from . import views

urlpatterns = [
    url(r'^dashboard/', views.dashboard, name='dashboard'),

    # 用户登陆
    url(r'login/', views.login, name='login'),
    # 用户退出
    url(r'logout/', views.logout, name='logout'),
    # 密码修改
    url(r'password_change/', views.password_change, name='password_change'),

    url(r'^ticket/ticket_list/', view_tickets.ticket_list, name='ticket_list'),
    url(r'^ticket/tickets_needfix/', view_tickets.tickets_needfix, name='tickets_needfix'),
    url(r'^ticket/ticket_needpay/', view_tickets.ticket_needpay, name='ticket_needpay'),
    url(r'^ticket/ticket_needcollect/', view_tickets.ticket_needcollect, name='ticket_needcollect'),
    url(r'^ticket/ticket_createorder/', view_tickets.ticket_createorder, name='ticket_createorder'),
    url(r'^ticket/ticket_payorders/', view_tickets.ticket_payorders, name='ticket_payorders'),
    url(r'^ticket/ticket_sellorders/', view_tickets.ticket_sellorders, name='ticket_sellorders'),
    url(r'^ticket/ticket_order/(?P<pk>\d+)/$', view_tickets.ticket_order, name='ticket_order'),
    url(r'^ticket/ticket_add/', view_tickets.ticket_add, name='ticket_add'),
    url(r'^ticket/ticket_import', view_tickets.ticket_import, name='ticket_import'),
    url(r'^ticket/flow_import', view_tickets.flow_import, name='flow_import'),
    url(r'^ticket/pool_import', views.pool_import, name='pool_import'),
    url(r'^ticket/ticket_index/(?P<pk>\d+)/$', view_tickets.ticket_index, name='ticket_index'),
    url(r'^loan/order/(?P<pk>\d+)/$', view_loan.loanorder, name='loanorder'),
    url(r'^loan/need_collect_customers/', view_loan.need_collect_customers, name='need_collect_customers'),
    url(r'^loan/need_pay_customers/', view_loan.need_pay_customers, name='need_pay_customers'),
    url(r'^loan/pre_collect_customers/', view_loan.pre_collect_customers, name='pre_collect_customers'),
    url(r'^loan/pre_pay_customers/', view_loan.pre_pay_customers, name='pre_pay_customers'),

    url(r'^loan/pre_collect_list/(?P<pk>\d+)/$', view_loan.pre_collect_list, name='pre_collect_list'),
    url(r'^loan/pre_pay_list/(?P<pk>\d+)/$', view_loan.pre_pay_list, name='pre_pay_list'),
    url(r'^loan/need_collect_lists/(?P<pk>\d+)/$', view_loan.need_collect_lists, name='need_collect_lists'),
    url(r'^loan/need_pay_lists/(?P<pk>\d+)/$', view_loan.need_pay_lists, name='need_pay_lists'),

    url(r'^pool/pool_dash/', view_pool.pool_dash, name='pool_dash'),
    url(r'^pool/pool_detail/(?P<pk>\d+)/$', view_pool.pool_detail, name='pool_detail'),
    url(r'^pool/pool_licai_lists/', view_pool.pool_licai_lists, name='pool_licai_lists'),
    url(r'^pool/super_loan_lists/', view_pool.super_loan_lists, name='super_loan_lists'),
    url(r'^pool/super_loan/(?P<pk>\d+)/$', view_pool.super_loan, name='pool_loan'),
    url(r'^pool/pool_tickets/', view_pool.pool_tickets, name='pool_tickets'),
    url(r'^pool/pool_percent_list/', view_pool.pool_percent_list, name='pool_percent_list'),
    url(r'^pool/pool_percent_detail/(?P<pk>\d+)/$', view_pool.pool_percent_detail, name='pool_percent_detail'),

    url(r'^card/card_list/', view_card.card_list, name='card_list'),
    url(r'^card/card_edit/(?P<pk>\d+)/$', view_card.card_edit, name='card_edit'),
    url(r'^card/card_trans/', view_card.card_trans, name='card_trans'),

    url(r'^log/log_list/', view_tools.log_list, name='log_list'),
    url(r'^download/dailyreport/', view_tools.daily_report, name='dailyreport'),

    url(r'^tool/bestmix/', view_tools.best_mix, name='bestmix'),
    url(r'^tool/avgday/', view_tools.avg_day, name='avgday'),
    url(r'^tool/tiexian/', view_tools.tiexian, name='tiexian'),

]