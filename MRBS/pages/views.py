from io import BytesIO

import folium
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q, Prefetch
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from django.shortcuts import render, get_list_or_404, redirect
from django.urls import resolve, reverse_lazy, reverse
from django.views import View
from django.views.generic import TemplateView, FormView
from openpyxl import Workbook

from .models import *
from .forms import *
from .api_waviot.functions import get_pu_info_extended, get_bs_info
from .data_analytics.functions import get_points_stat, get_department_info, get_department_bs_info, get_pu_parse_count, \
    map_generator, get_count_devicehistory_by_address_point, group_by_percentage, get_xlsx_report, \
    file_upload_processing, list_upload_devices_reports


# Create your views here.


class MRBSBasic(LoginRequiredMixin, TemplateView):
    extra_context = {
        'title': 'Мониторинг работы УСПД',
        'header': 'Мониторинг работы УСПД',
    }

    def is_in_group(self, group_name):
        return self.request.user.groups.filter(name=group_name).exists()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Получаем имя текущего маршрута
        resolved_url = resolve(self.request.path)
        context['current_urlname'] = resolved_url.url_name
        context['add_device_access'] = self.is_in_group('AddDeviceAccess')

        return context


class MRBSDataOverview(MRBSBasic):
    template_name = 'pages/data-overview-all.html'

    # def dispatch(self, request, *args, **kwargs):
    #     if not self.request.user.is_authenticated:
    #         return redirect('users:login')
    #     user_dep = self.request.user.department
    #     if not user_dep == 'Аппарат Управления':
    #         if DepartmentList.objects.filter(name=user_dep).exists():
    #             url = reverse('data-overview-one', kwargs={'pk': DepartmentList.objects.get(name=user_dep).pk})
    #             return HttpResponseRedirect(url)
    #         else:
    #             return super().dispatch(request, *args, **kwargs)
    #     else:
    #         return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Получаем имя текущего маршрута
        resolved_url = resolve(self.request.path)
        context['current_urlname'] = resolved_url.url_name
        context['add_device_access'] = self.is_in_group('AddDeviceAccess')

        last_bs_parses = ParseHistory.objects.filter(parse_type__name='Опрос БС').order_by('-parse_end_time')[:10]
        last_bs_parses = list(reversed(last_bs_parses))
        last_pu_parses = ParseHistory.objects.filter(parse_type__name='Опрос ПУ').order_by('-parse_end_time')[:10]
        last_pu_parses = list(reversed(last_pu_parses))

        context['last_bs_parses'] = last_bs_parses
        context['last_pu_parses'] = last_pu_parses

        dep_list = DepartmentList.objects.all().order_by('name')

        context['count_pu'] = Device.objects.all().count()
        context['count_bs'] = BaseStation.objects.all().count()
        context['count_points'] = AddressPoint.objects.all().count()

        context['all_dep_counts_info'] = get_department_info(dep_list)
        context['all_dep_bs_last_parses'] = get_department_bs_info(dep_list, last_bs_parses)
        context['all_dep_devices_history'] = get_pu_parse_count(last_pu_parses)

        last_pu_parses_ps = ParseHistory.objects.filter(parse_type__name='Опрос ПУ').order_by('-parse_end_time')[:3]
        last_pu_parses_ps = list(reversed(last_pu_parses_ps))
        context['all_dep_points_stat'] = get_points_stat(last_pu_parses_ps)

        return context


class MRBSDataOverviewOne(MRBSBasic):
    template_name = 'pages/data-overview-one.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Получаем имя текущего маршрута
        resolved_url = resolve(self.request.path)
        context['current_urlname'] = resolved_url.url_name
        context['add_device_access'] = self.is_in_group('AddDeviceAccess')

        last_bs_parses = ParseHistory.objects.filter(parse_type__name='Опрос БС').order_by('-parse_end_time')[:10]
        last_bs_parses = list(reversed(last_bs_parses))
        last_pu_parses = ParseHistory.objects.filter(parse_type__name='Опрос ПУ').order_by('-parse_end_time')[:10]
        last_pu_parses = list(reversed(last_pu_parses))

        context['last_bs_parses'] = last_bs_parses
        context['last_pu_parses'] = last_pu_parses

        request_dep = DepartmentList.objects.get(pk=self.kwargs['pk'])
        context['request_dep'] = request_dep

        context['count_pu'] = Device.objects.filter(department=request_dep).count()
        context['count_bs'] = BaseStation.objects.filter(department=request_dep).count()
        context['count_points'] = AddressPoint.objects.filter(department=request_dep).count()

        context['dep_bs_last_parses'] = get_department_bs_info(DepartmentList.objects.filter(pk=self.kwargs['pk']), last_bs_parses)
        context['dep_devices_history'] = get_pu_parse_count(last_pu_parses, request_dep=request_dep)

        last_pu_parses_ps = ParseHistory.objects.filter(parse_type__name='Опрос ПУ').order_by('-parse_end_time')[:3]
        last_pu_parses_ps = list(reversed(last_pu_parses_ps))
        context['dep_points_stat'] = get_points_stat(last_pu_parses_ps, request_dep=request_dep)

        return context


class MRBSBaseStations(MRBSBasic):
    template_name = 'pages/base-stations.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Получаем имя текущего маршрута
        resolved_url = resolve(self.request.path)
        context['current_urlname'] = resolved_url.url_name
        context['add_device_access'] = self.is_in_group('AddDeviceAccess')

        if self.request.user.department == 'Аппарат Управления':
            context['all_stations'] = BaseStation.objects.all().order_by('department__name', 'station_number')
        else:
            context['all_stations'] = BaseStation.objects.filter(department__name=self.request.user.department).order_by('department__name', 'station_number')
        return context


class MRBSBaseStationInfo(MRBSBasic):
    template_name = 'pages/base-station-info.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Получаем имя текущего маршрута
        resolved_url = resolve(self.request.path)
        context['current_urlname'] = resolved_url.url_name
        context['add_device_access'] = self.is_in_group('AddDeviceAccess')

        context['base_station_info'] = BaseStation.objects.get(pk=self.kwargs['pk'])
        context['base_station_history'] = BaseStationHistory.objects.filter(basestation=BaseStation.objects.get(pk=self.kwargs['pk'])).order_by('-parse_history__parse_end_time')[:10]

        return context


class MRBSHelpPage(MRBSBasic):
    template_name = 'pages/help.html'


class MRBSChangeHistory(MRBSBasic):
    template_name = 'pages/change-history.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Получаем имя текущего маршрута
        resolved_url = resolve(self.request.path)
        context['current_urlname'] = resolved_url.url_name
        context['add_device_access'] = self.is_in_group('AddDeviceAccess')

        context['changes_history'] = ChangeHistory.objects.all()

        return context


class MRBSRezervPage(MRBSBasic):
    template_name = 'pages/rezerv.html'


class MRBSDataOnMap(MRBSBasic):
    template_name = 'pages/data-on-map.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Получаем имя текущего маршрута
        resolved_url = resolve(self.request.path)
        context['current_urlname'] = resolved_url.url_name
        context['add_device_access'] = self.is_in_group('AddDeviceAccess')

        map_object = map_generator(None, self.request.user.department)
        context['map'] = map_object['map']
        context['map_description'] = map_object['map_description']

        return context


def get_data_on_map(request):
    if request.method == 'GET':
        map_type = request.GET['map_type']
        if not request.user.is_authenticated:
            return redirect('users:login')
        user_dep = request.user.department
        if map_type is not None:
            map_object = map_generator(map_type, user_dep)
            return render(request, 'pages/data-on-map-part.html',
                          {'map': map_object['map'],
                           'map_description': map_object['map_description'],
                           })
        else:
            return redirect('users:login')


class MRBSDeviceAdd(MRBSBasic, FormView):
    form_class = FileUploadForm
    template_name = 'pages/device-add.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Получаем имя текущего маршрута
        resolved_url = resolve(self.request.path)
        context['current_urlname'] = resolved_url.url_name
        context['add_device_access'] = self.is_in_group('AddDeviceAccess')

        context['list_reports'] = list_upload_devices_reports()

        return context

@login_required
def add_device(request):
    if request.method == 'POST':
        uploaded_file = request.FILES['uploaded_file']
        report_file = file_upload_processing(uploaded_file)
        if report_file['result']:
            return JsonResponse({'status': True,
                                 'message': f'../media/upload_devices_reports/{report_file['filename']}'
                                 }, status=200)
        else:
            return JsonResponse({'status': False}, status=200)
    else:
        return JsonResponse({'error': 'Нет файла'}, status=400)


class MRBSInfoDevicePage(MRBSBasic, FormView):
    form_class = DeviceSearchForm
    success_url = reverse_lazy('info-device')
    template_name = 'pages/info-device.html'


@login_required
def get_device_info(request):
    search_field = request.GET['search_field']
    try:
        search_device = Device.objects.select_related('department').get(serial_number=search_field)
        device_stat = DeviceHistory.objects.filter(device=search_device).order_by('-last_record_time', '-parse_history__parse_end_time')[:10]
        return render(request, 'pages/tables/info-device-tables.html',
                      {'request_device': search_device,
                       'device_stat': device_stat,
                       'received': True,
                       })
    except Device.DoesNotExist:
        return render(request, 'pages/tables/info-device-tables.html',
                      {'received': False,
                       })


class MRBSAddressPointStat(MRBSBasic, FormView):
    form_class = AddressSearchForm
    success_url = reverse_lazy('address-points-stat')
    template_name = 'pages/address-points-stat.html'


@login_required
def get_address_list(request):
    search_field = request.GET['search_field']
    # или ФИАС или адрес строения
    if request.user.department == 'Аппарат Управления':
        search_address = AddressPoint.objects.filter(Q(fias__icontains=search_field) |
                                                     Q(building_address__icontains=search_field)).annotate(
            device_count=Count('device')).order_by('-device_count')
    else:
        search_address = AddressPoint.objects.filter(Q(fias__icontains=search_field) |
                                                     Q(building_address__icontains=search_field),
                                                     department__name=request.user.department).annotate(
            device_count=Count('device')).order_by('-device_count')
    if search_address:
        return render(request, 'pages/tables/address-points-stat-tables.html',
                      {'request_address': search_address,
                       'received': True,
                       })
    else:
        return render(request, 'pages/tables/address-points-stat-tables.html',
                      {'received': False,
                       })


class MRBSServerParse(MRBSBasic):
    template_name = 'pages/server-parse.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Получаем имя текущего маршрута
        resolved_url = resolve(self.request.path)
        context['current_urlname'] = resolved_url.url_name
        context['add_device_access'] = self.is_in_group('AddDeviceAccess')
        context['parse_access'] = self.is_in_group('ParseAccess')

        context['request_bs_history'] = ParseHistory.objects.filter(parse_type__name='Опрос БС').order_by('-parse_end_time')[:5]
        context['request_pu_history'] = ParseHistory.objects.filter(parse_type__name='Опрос ПУ').annotate(
            device_count=Count('devicehistory')).order_by('-parse_end_time')[:5]
        context['parse_status_bs'] = ParseTemp.objects.get(name='Опрос БС')
        context['parse_status_pu'] = ParseTemp.objects.get(name='Опрос ПУ')
        return context


@login_required
def start_server_request(request):
    if request.method == 'POST':
        if request.POST['request_type'] == 'startPU':
            if ParseTemp.objects.get(name='Опрос ПУ').status:
                return JsonResponse({'success': False,
                                     })
            else:
                changed_parse_object = ParseTemp.objects.get(name='Опрос ПУ')
                changed_parse_object.status = True
                changed_parse_object.save()
                if get_pu_info_extended('Ручной опрос приборов учета'):
                # if get_pu_info('Ручной опрос приборов учета'):
                    changed_parse_object.status = False
                    changed_parse_object.save()
                    return JsonResponse({'success': True,
                                         })
        elif request.POST['request_type'] == 'startBS':
            if ParseTemp.objects.get(name='Опрос БС').status:
                return JsonResponse({'success': False,
                                     })
            else:
                changed_parse_object = ParseTemp.objects.get(name='Опрос БС')
                changed_parse_object.status = True
                changed_parse_object.save()
                if get_bs_info('Ручной опрос базовых станций'):
                    changed_parse_object.status = False
                    changed_parse_object.save()
                    return JsonResponse({'success': True,
                                         })


class MRBSParsePuHistoryAllDep(MRBSBasic):
    template_name = 'pages/server-parse-hpu.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Получаем имя текущего маршрута
        resolved_url = resolve(self.request.path)
        context['current_urlname'] = resolved_url.url_name
        context['add_device_access'] = self.is_in_group('AddDeviceAccess')

        request_parse = ParseHistory.objects.filter(pk=self.kwargs['pk'])

        dep_list = DepartmentList.objects.all().order_by('name')

        context['all_dep_points_stat'] = get_points_stat(request_parse)
        all_dep_points_stat_for_parse = []
        for dep in dep_list:
            one_stat = get_points_stat(request_parse, request_dep=dep)
            all_dep_points_stat_for_parse.append(
                {
                    'department': dep,
                    'stat': one_stat,
                }
            )
        context['count_pu'] = Device.objects.all().count()
        context['request_parse_object'] = request_parse[0]
        context['all_pu_parse_count_history'] = get_pu_parse_count(request_parse)[0]
        context['all_dep_points_stat_for_parse'] = all_dep_points_stat_for_parse
        dep_list = DepartmentList.objects.all().order_by('name')
        all_dep_devices_history = []
        for dep in dep_list:
            dep_devices_history = get_pu_parse_count(request_parse, request_dep=dep)[0]
            all_dep_devices_history.append(
                {
                    'department': dep,
                    'parse_count_devices': dep_devices_history,
                    'count_devices': Device.objects.filter(department=dep).count()
                }
            )
        context['all_dep_devices_history'] = all_dep_devices_history
        return context


class MRBSAddressPointInfo(MRBSBasic):
    template_name = 'pages/address-point-info.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Получаем имя текущего маршрута
        resolved_url = resolve(self.request.path)
        context['current_urlname'] = resolved_url.url_name
        context['add_device_access'] = self.is_in_group('AddDeviceAccess')

        context['fias_info'] = AddressPoint.objects.annotate(device_count=Count('device')).get(pk=self.kwargs['pk'])
        devices = list(Device.objects.filter(fias=self.kwargs['pk']))
        last_parsers = ParseHistory.objects.filter(parse_type__name='Опрос ПУ').order_by('-parse_end_time')[:3]
        last_parsers = list(reversed(last_parsers))
        # for device in devices:
        #     histories = []
        #     for every in last_parsers:
        #         try:
        #             last_record_time = DeviceHistory.objects.get(parse_history=every, device=device)
        #             histories.append(last_record_time)
        #         except DeviceHistory.DoesNotExist:
        #             histories.append(None)
        #     setattr(device, 'histories', histories)

        # КОД ГИГАЧАТА

        devices = Device.objects.filter(fias=context['fias_info']).prefetch_related(
            Prefetch(
                'devicehistory_set',
                queryset=DeviceHistory.objects.filter(parse_history__in=last_parsers),
                to_attr='prefetched_histories'
            )
        )

        # Сбор необходимой информации
        for device in devices:
            histories = []
            for parser in last_parsers:
                # Поиск конкретной истории для заданного парсера
                found_history = next((dh for dh in device.prefetched_histories if dh.parse_history == parser), None)
                histories.append(found_history)

            # Привязываем собранные истории к устройству
            setattr(device, 'histories', histories)

        context['fias_devices'] = devices
        context['last_parsers'] = last_parsers

        return context


class MRBSDownloadXLSXReport(View):
    def get(self, request, report_type, request_dep, parse_object, *args, **kwargs):
        response = get_xlsx_report(report_type, request_dep, parse_object)
        return response


# ниже находятся служебные FBV
def device_input(request):
    if request.method == 'POST':
        with open('C:\\Users\\kuramshin_ra\\Documents\\python_projects\\WaviotMonitor\\MRBS\\all_dev_info.csv', 'r',
                  encoding='utf-8') as device_file:
            for line in device_file:
                device_parts = line.strip().split(';')
                building_address = AddressPoint.objects.get(building_address=device_parts[3])
                new_device = Device(department=device_parts[0],
                                    serial_number=device_parts[1],
                                    variety=device_parts[2],
                                    fias=AddressPoint.objects.get(pk=building_address.pk),
                                    address_1c=device_parts[5],
                                    )
                new_device.save()

    return render(request, 'pages/create.html')


def department_normalize(request):
    if request.method == 'POST':
        # ДЛЯ ТАБЛИЦЫ AddressPoint
        # with open('C:\\Users\\kuramshin_ra\\Documents\\python_projects\\WaviotMonitor\\MRBS\\new_address_point.csv', 'r', encoding='utf-8') as point_list:
        #     for line in point_list:
        #         address_parts = line.strip().split(';')
        #         if 'Моршанск' in address_parts[0]:
        #             depart_clear = DepartmentList.objects.get(name='Моршанск')
        #         elif 'Тамбов' in address_parts[0]:
        #             depart_clear = DepartmentList.objects.get(name='Тамбов')
        #         elif 'Мичуринск' in address_parts[0]:
        #             depart_clear = DepartmentList.objects.get(name='Мичуринск')
        #         elif 'Кирсанов' in address_parts[0]:
        #             depart_clear = DepartmentList.objects.get(name='Кирсанов')
        #         elif 'Жердевк' in address_parts[0]:
        #             depart_clear = DepartmentList.objects.get(name='Жердевк')
        #         elif 'Уваров' in address_parts[0]:
        #             depart_clear = DepartmentList.objects.get(name='Уваров')
        #         elif 'Рассказов' in address_parts[0]:
        #             depart_clear = DepartmentList.objects.get(name='Рассказов')
        #         elif 'Котовск' in address_parts[0]:
        #             depart_clear = DepartmentList.objects.get(name='Котовск')
        #         updated_point = AddressPoint.objects.get(building_address=address_parts[2])
        #         updated_point.department = depart_clear
        #         updated_point.save()
        # ДЛЯ ТАБЛИЦЫ Device
        # all_devices = Device.objects.all()
        # for device in all_devices:
        #     if 'Моршанск' in device.department:
        #         depart_clear = DepartmentList.objects.get(name='Моршанск')
        #     elif 'Тамбов' in device.department:
        #         depart_clear = DepartmentList.objects.get(name='Тамбов')
        #     elif 'Мичуринск' in device.department:
        #         depart_clear = DepartmentList.objects.get(name='Мичуринск')
        #     elif 'Кирсанов' in device.department:
        #         depart_clear = DepartmentList.objects.get(name='Кирсанов')
        #     elif 'Жердевк' in device.department:
        #         depart_clear = DepartmentList.objects.get(name='Жердевк')
        #     elif 'Уваров' in device.department:
        #         depart_clear = DepartmentList.objects.get(name='Уваров')
        #     elif 'Рассказов' in device.department:
        #         depart_clear = DepartmentList.objects.get(name='Рассказов')
        #     elif 'Котовск' in device.department:
        #         depart_clear = DepartmentList.objects.get(name='Котовск')
        #     device.dep_clear = depart_clear
        #     device.save()
        print()

    return render(request, 'pages/create.html')
