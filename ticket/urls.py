from django.conf.urls import url
from . import views

urlpatterns = [
    # url(r'^$', views.index, name='index'),
    # url(r'^upa/', views.upfile, name='upfile'),
    # url(r'^up/', views.indexa, name='upfile'),
    # url(r'^ticket_add/', views.ticket_add, name='ticket_add'),
    url(r'^dashboard/', views.dashboard, name='dashboard'),
    url(r'^sysconfig/inpoolPercent', views.inpoolPercent, name='inpoolPercent'),

    # 用户登陆列表
    # 用户登陆
    url(r'login/', views.login, name='login'),
    # 用户退出
    url(r'logout/', views.logout, name='logout'),
    # 密码修改
    url(r'password_change/', views.password_change, name='password_change'),

    # 任务列表
    url(r'^ticket/ticket_list/', views.ticket_list, name='ticket_list'),
    url(r'^ticket/tickets_needfix/', views.tickets_needfix, name='tickets_needfix'),
    url(r'^ticket/ticket_needpay/', views.ticket_needpay, name='ticket_needpay'),
    url(r'^ticket/ticket_needcollect/', views.ticket_needcollect, name='ticket_needcollect'),
    url(r'^ticket/ticket_createorder/', views.ticket_createorder, name='ticket_createorder'),
    # url(r'^ticket/ticket_createorder/', views.ticket_createorder, name='ticket_createorder'),
    url(r'^order/ticket_payorders/', views.ticket_payorders, name='ticket_payorders'),
    url(r'^order/ticket_payorder/(?P<pk>\d+)/$', views.ticket_payorder, name='ticket_payorder'),
    url(r'^order/ticket_sellorders/', views.ticket_sellorders, name='ticket_sellorders'),
    url(r'^order/ticket_sellorder/(?P<pk>\d+)/$', views.ticket_sellorder, name='ticket_sellorder'),
    url(r'^ticket/ticket_add/', views.ticket_add, name='ticket_add'),
    url(r'^ticket/ticket_import', views.ticket_import, name='ticket_import'),
    url(r'^ticket/flow_import', views.flow_import, name='flow_import'),
    url(r'^ticket/pool_import', views.pool_import, name='pool_import'),
    url(r'^ticket/ticket_index/(?P<pk>\d+)/$', views.ticket_index, name='ticket_index'),
    url(r'^ticket/ticket_fix/', views.ticket_fix, name='ticket_fix'),
    # url(r'^ticket_delete/(?P<pk>\d+)/$', views.ticket_delete, name='ticket_delete'),
    # url(r'^ticket_finish/(?P<pk>\d+)/$', views.ticket_finish, name='ticket_finish'),
    url(r'^loan/borrow_status/', views.borrow_status, name='borrow_status'),
    url(r'^loan/loan_status/', views.loan_status, name='loan_status'),
    url(r'^loan/borrow_list/', views.borrow_list, name='borrow_list'),
    url(r'^loan/loan_list/', views.loan_list, name='loan_list'),
    url(r'^loan/order/(?P<pk>\d+)/$', views.loanorder, name='loanorder'),

    url(r'^card/card_list/', views.card_list, name='card_list'),
    url(r'^card/card_add/', views.card_add, name='card_add'),
    url(r'^card/card_edit/(?P<pk>\d+)/$', views.card_edit, name='card_edit'),
    # url(r'^card/card_delete/(?P<pk>\d+)/$', views.ticket_delete, name='ticket_delete'),
    url(r'^card/card_index/(?P<pk>\d+)/$', views.card_edit, name='card_index'),
    url(r'^card/card_trans/', views.card_trans, name='card_trans'),

    url(r'^pool/pool_dash/', views.pool_dash, name='pool_dash'),
    url(r'^pool/pool_pro/', views.pool_pro, name='pool_pro'),
    url(r'^pool/pool_loans/', views.pool_loans, name='pool_loans'),
    url(r'^pool/pool_loan/(?P<pk>\d+)/$', views.pool_loan, name='pool_loan'),
    url(r'^pool/pool_loan_repay/', views.pool_loan_repay, name='pool_loan_repay'),
    url(r'^pool/pool_tickets/', views.pool_tickets, name='pool_tickets'),
    # url(r'^card/card_add/', views.card_add, name='card_add'),
    # url(r'^card/card_edit/(?P<pk>\d+)/$', views.card_edit, name='card_edit'),
    # url(r'^card/card_delete/(?P<pk>\d+)/$', views.ticket_delete, name='ticket_delete'),
    # url(r'^card/card_index/(?P<pk>\d+)/$', views.card_edit, name='card_index'),

    url(r'^log/log_list/', views.log_list, name='log_list'),

    url(r'^tool/bestmix/', views.bestmix, name='bestmix'),
    url(r'^tool/avgday/', views.avgday, name='avgday'),
    url(r'^tool/counter/', views.counter, name='counter'),

]