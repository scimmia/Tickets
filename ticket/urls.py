from django.conf.urls import url
from . import views

urlpatterns = [
    # url(r'^$', views.index, name='index'),
    # url(r'^upa/', views.upfile, name='upfile'),
    # url(r'^up/', views.indexa, name='upfile'),
    # url(r'^ticket_add/', views.ticket_add, name='ticket_add'),
    url(r'^dashboard/', views.dashboard, name='dashboard'),

    # 用户登陆列表
    # 用户登陆
    url(r'login/', views.login, name='login'),
    # 用户退出
    url(r'logout/', views.logout, name='logout'),
    # 密码修改
    url(r'password_change/', views.password_change, name='password_change'),

    # 任务列表
    url(r'^ticket/ticket_list/', views.ticket_list, name='ticket_list'),
    url(r'^ticket/ticket_add/', views.ticket_add, name='ticket_add'),
    # url(r'^ticket_edit/(?P<pk>\d+)/$', views.ticket_edit, name='ticket_edit'),
    # url(r'^ticket_delete/(?P<pk>\d+)/$', views.ticket_delete, name='ticket_delete'),
    # url(r'^ticket_finish/(?P<pk>\d+)/$', views.ticket_finish, name='ticket_finish'),

    url(r'^card/card_list/', views.card_list, name='card_list'),
    url(r'^card/card_add/', views.card_add, name='card_add'),
    url(r'^card/card_edit/(?P<pk>\d+)/$', views.card_edit, name='card_edit'),
    # url(r'^card/card_delete/(?P<pk>\d+)/$', views.ticket_delete, name='ticket_delete'),
    url(r'^card/card_index/(?P<pk>\d+)/$', views.card_edit, name='card_index'),

]