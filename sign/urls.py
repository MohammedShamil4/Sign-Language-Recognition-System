from django.urls import path

from sign import views

urlpatterns = [
    path('', views.main, name='main'),
    path('logins', views.logins, name='logins'),
    path('approve_p', views.approve_p, name='approve_p'),
    path('manage_p', views.manage_p, name='manage_p'),
    path('tip', views.tip, name='tip'),
    path('sm', views.sm, name='sm'),
    path('stm', views.stm, name='stm'),
    path('ad_sm', views.ad_sm, name='ad_sm'),
    path('ad_stm', views.ad_stm, name='ad_stm'),
    path('rt', views.rt, name='rt'),
    path('ub', views.ub, name='ub'),
    path('ubs', views.ubs, name='ubs'),
    path('block_parent/<int:id>', views.block_parent, name='block_parent'),
    path('block_staff/<int:id>', views.block_staff, name='block_staff'),
    path('unblock_parent/<int:id>', views.unblock_parent, name='unblock_parent'),
    path('unblock_staff/<int:id>', views.unblock_staff, name='unblock_staff'),
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
    path('up_s', views.up_s, name='up_s'),
    path('pt_hm', views.pt_hm, name='pt_hm'),
    path('mg_w', views.mg_w, name='mg_w'),
    path('up_w', views.up_w, name='up_w'),
    path('st_c', views.st_c, name='st_c'),
    path('st_cc/<int:id>', views.st_cc, name='st_cc'),
    path('pt_cc/<int:id>', views.pt_cc, name='pt_cc'),
    path('chat_s', views.chat_s, name='chat_s'),
    path('red_c', views.red_c, name='red_c'),
    path('chat_p', views.chat_p, name='chat_p'),
    path('rd_c', views.rd_c, name='rd_c'),
    path('rmg', views.rmg, name='rmg'),
    path('sr', views.sr, name='sr'),
    path('update_tp/<int:id>', views.update_tp, name='update_tp'),
    path('u_tp', views.u_tp, name='u_tp'),
    path('delete_tip/<int:id>', views.delete_tip, name='delete_tip'),
    path('pc', views.pc, name='pc'),
    path('up_mts/<int:id>', views.up_mts, name='up_mts'),
    path('up_ms', views.up_ms, name='up_ms'),
    path('dlt_study/<int:id>', views.dlt_study, name='dlt_study'),
    path('ad_tp', views.ad_tp, name='ad_tp'),
    path('std_reg', views.std_reg, name='std_reg'),
    path('insert_st', views.insert_st, name='insert_st'),
    path('pts_hm', views.pts_hm, name='pts_hm'),
    path('logout', views.logout, name='logout'),
    path('sen_r', views.sen_r, name='sen_r'),
    path('ad_vrg', views.ad_vrg, name='ad_vrg'),
    path('up_cw', views.up_cw, name='up_cw'),
    path('update_cw/<int:id>', views.update_cw, name='update_cw'),
    # path('gest', views.gest, name='gest'),
    path('updt_cw', views.updt_cw, name='updt_cw'),
    path('dlt_work/<int:id>', views.dlt_work, name='dlt_work'),
    path('feeds', views.feeds, name='feeds'),
    path('s_feed/<int:id>', views.s_feed, name='s_feed'),
    path('s_fd', views.s_fd, name='s_fd'),
    path('class_wk', views.class_wk, name='class_wk'),
    path('class_w', views.class_w, name='class_w'),
    path('v_fd', views.v_fd, name='v_fd'),
    path('st_rev', views.st_rev, name='st_rev'),
    path('texts', views.texts, name='texts'),
    path('translate_text', views.translate_text, name='translate_text'),
]
