from django.urls import path
from . import views
from .views_dir import login_views, report_views, data_import_views, crypto_views, set_api_views, actionzone

urlpatterns = [
    # login
    path('', login_views.home_view, name='home'),
    path('login/', login_views.login_view, name='login'),
    path('logout/', login_views.logout_view, name='logout'),

    # dashboard
    path('home/', report_views.home, name='home'), 

    # report menu
    path('inc_exp_report/', report_views.inc_exp_report, name='inc_exp_report'),
    path('report_by_range/', report_views.report_by_range, name='report_by_range'),
    path('monthly_report/', report_views.monthly_report_view, name='monthly_report_view'),
    path('yearly_report/', report_views.yearly_report, name='yearly_report'),

    # data setting menu
    path('convert_moneydance/', data_import_views.convert_moneydance, name='convert_moneydance'),
    path('get_dataset/', data_import_views.get_dataset, name='get_dataset'),
    path('set_selection/', data_import_views.set_selection, name='set_selection'),
    path('set_tier/', data_import_views.set_tier, name='set_tier'),

    # data crypto - get portfolio from Bitkub
    path('crypto/', crypto_views.wallet_balances, name='crypto'),
    path('deposit_history/', crypto_views.deposit_history, name='deposit_history'),
    path('deposit_history_bitkub/', crypto_views.deposit_history_bitkub, name='deposit_history_bitkub'),
    path('deposit_history_binanceth/', crypto_views.deposit_history_binanceth, name='deposit_history_binanceth'),

    path('purchased_report_page/', crypto_views.purchased_report_page, name='purchased_report_page'),
    path('purchased_report/', crypto_views.purchased_report, name='purchased_report'),  # JSON API

    # n8n-BITKUB http-request method
    # path('n8n-btc-trigger/', crypto_views.n8n_btc_trigger, name='n8n_btc_trigger'),
    # path('n8n-eth-trigger/', crypto_views.n8n_eth_trigger, name='n8n_eth_trigger'),
    path('n8n-trigger/', crypto_views.n8n_trigger, name='n8n_trigger'), # this url is send various Symbol and Amount
    path('place_bid/', crypto_views.place_order, name='place_bid'),

    # n8n Chaloke Action Zone 
    path('n8n-actionzone-symbol/', actionzone.n8n_actionzone_symbol, name='n8n_actionzone_symbol'),
    path('n8n-actionzone-execute/', actionzone.n8n_actionzone_execute, name='n8n_actionzone_execute'),
    
    # data set api
    path('set_api/', set_api_views.portfolio, name='set_api'),
    # path('set_purchased_report_page/', set_api_views.set_purchased_report_page, name='set_purchased_report_page'),

    # n8n-SET http-request method
    path('n8n-set-trigger/', set_api_views.n8n_set_trigger, name='n8n_set_trigger'), 
    path('n8n-update_stock_purchased/', set_api_views.n8n_update_stock_purchased, name='n8n_update_stock_purchased'), 
    # purchase stock via API -> KBANK,BBL,SCB, APPL80, GOOG80, META01, MFST80
    

]

# handler404 = 'moneydance.views.custom_404'
# handler500 = 'moneydance.views.custom_500'