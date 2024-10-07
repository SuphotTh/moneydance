from django.urls import path
from . import views
from .views_dir import login_views, report_views, data_import_views


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
]