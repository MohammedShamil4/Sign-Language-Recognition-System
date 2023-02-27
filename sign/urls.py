from django.urls import path

from sign import views

urlpatterns = [
    path('', views.main, name='main'),
    path('approve_p', views.approve_p, name='approve_p'),
    path('manage_p', views.manage_p, name='manage_p'),
    path('tip', views.tip, name='tip'),
    path('sm', views.sm, name='sm'),
    path('rt', views.rt, name='rt'),
    path('ub', views.ub, name='ub'),
    path('manage_s', views.manage_s, name='manage_s'),
    path('adm', views.adm, name='adm'),
    path('log', views.log, name='log'),
    path('st_reg', views.st_reg, name='st_reg'),
    path('reg_stf', views.reg_stf, name='reg_stf'),
    path('update_st/<int:id>', views.update_st, name='update_st'),
    path('delete_st/<int:id>', views.delete_st, name='delete_st'),
    path('apr/<int:id>', views.apr, name='apr'),
    path('rej_p/<int:id>', views.rej_p, name='rej_p'),
    path('up_st', views.up_st, name='up_st'),
    path('sth', views.sth, name='sth'),
    path('reg_pt', views.reg_pt, name='reg_pt'),
    path('reg_p', views.reg_p, name='reg_p'),
    path('vp', views.vp, name='vp'),
    path('mg_tp', views.mg_tp, name='mg_tp'),
    path('ad_t', views.ad_t, name='ad_t'),
    path('tp', views.tp, name='tp'),
    path('upload_s', views.upload_s, name='upload_s'),
]
