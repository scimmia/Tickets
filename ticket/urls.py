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
    url(r'^ticket/ticket_needpay/', views.ticket_needpay, name='ticket_needpay'),
    url(r'^ticket/ticket_needcollect/', views.ticket_needcollect, name='ticket_needcollect'),
    url(r'^ticket/ticket_topay/', views.ticket_topay, name='ticket_topay'),
    url(r'^ticket/ticket_createorder/', views.ticket_createorder, name='ticket_createorder'),
    url(r'^ticket/ticket_payorder/(?P<pk>\d+)/$', views.ticket_payorder, name='ticket_payorder'),
    url(r'^ticket/ticket_add/', views.ticket_add, name='ticket_add'),
    url(r'^ticket/ticket_import', views.ticket_import, name='ticket_import'),
    url(r'^ticket/ticket_index/(?P<pk>\d+)/$', views.ticket_index, name='ticket_index'),
    url(r'^ticket/ticket_edit/(?P<pk>\d+)/$', views.ticket_edit, name='ticket_edit'),
    # url(r'^ticket_delete/(?P<pk>\d+)/$', views.ticket_delete, name='ticket_delete'),
    # url(r'^ticket_finish/(?P<pk>\d+)/$', views.ticket_finish, name='ticket_finish'),

    url(r'^card/card_list/', views.card_list, name='card_list'),
    url(r'^card/card_add/', views.card_add, name='card_add'),
    url(r'^card/card_edit/(?P<pk>\d+)/$', views.card_edit, name='card_edit'),
    # url(r'^card/card_delete/(?P<pk>\d+)/$', views.ticket_delete, name='ticket_delete'),
    url(r'^card/card_index/(?P<pk>\d+)/$', views.card_edit, name='card_index'),

    url(r'^pool/pool_dash/', views.pool_dash, name='pool_dash'),
    url(r'^pool/pool_pro/', views.pool_pro, name='pool_pro'),
    # url(r'^card/card_add/', views.card_add, name='card_add'),
    # url(r'^card/card_edit/(?P<pk>\d+)/$', views.card_edit, name='card_edit'),
    # url(r'^card/card_delete/(?P<pk>\d+)/$', views.ticket_delete, name='ticket_delete'),
    # url(r'^card/card_index/(?P<pk>\d+)/$', views.card_edit, name='card_index'),

]