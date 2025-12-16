from django.conf import settings
from django.urls import path
from django.shortcuts import redirect
from . import views


urlpatterns = [
    path('', lambda request: redirect('data-overview', permanent=True)),
    path('data-overview/', views.MRBSDataOverview.as_view(), name='data-overview'),
    path('data-overview/<int:pk>/', views.MRBSDataOverviewOne.as_view(), name='data-overview-one'),
    path('base-stations/', views.MRBSBaseStations.as_view(), name='base-stations'),
    path('base-stations/base-station/<int:pk>/', views.MRBSBaseStationInfo.as_view(), name='base-station-info'),
    path('help/', views.MRBSHelpPage.as_view(), name='help'),
    path('change-history/', views.MRBSChangeHistory.as_view(), name='change-history'),
    path('rezerv/', views.MRBSRezervPage.as_view(), name='rezerv'),
    path('info-device/', views.MRBSInfoDevicePage.as_view(), name='info-device'),
    path('info-device/get-device-info/', views.get_device_info, name='get-device-info'),
    path('address-points-stat/', views.MRBSAddressPointStat.as_view(), name='address-points-stat'),
    path('address-points-stat/get-address-list/', views.get_address_list, name='get-address-list'),
    path('address-points-stat/address-point-info/<int:pk>/', views.MRBSAddressPointInfo.as_view(), name='address-point-info'),
    path('server-parse/', views.MRBSServerParse.as_view(), name='server-parse'),
    path('server-parse/start/', views.start_server_request, name='server-parse-start'),
    path('parse-view/<int:pk>/', views.MRBSParsePuHistoryAllDep.as_view(), name='parse-view-all'),
    path('data-on-map/', views.MRBSDataOnMap.as_view(), name='data-on-map'),
    path('data-on-map/map-request/', views.get_data_on_map, name='data-on-map-request'),
    path('device-add/', views.MRBSDeviceAdd.as_view(), name='device-add'),
    path('device-add/load/', views.add_device, name='device-add-load'),
    path('maintenance/', views.MRBSMaintenancePage.as_view(), name='maintenance'),
    path('maintenance/reload-wm/', views.reload_waviot_monitor, name='maintenance-reload'),
    path('download/xlsx/<slug:report_type>/<int:request_dep>/<int:parse_object>/', views.MRBSDownloadXLSXReport.as_view(), name='download-report-xlsx'),
    # path('create/', views.device_input, name='create'),
    # path('create/', views.department_normalize, name='department_normalize'),
]

# start-request server-parse