import os
import re
from io import BytesIO
from urllib.parse import quote

import folium
from django.conf import settings
from django.db.models import Q, Count, Prefetch
from django.http import HttpResponse
from folium.plugins import MarkerCluster, HeatMap
from openpyxl import Workbook
from dadata import Dadata

from ..models import *


def get_count_devicehistory_by_address_point(parse_history, **kwargs):
    """ Функция возвращает словарь с числом записей DeviceHistory, сгруппированных по каждому AddressPoint для
    заданной записи ParseHistory, с общим числом ПУ на каждом AddressPoint, а так же их процентное соотношение,
    в отсортированном по процентам виде"""
    selected_dep = kwargs.pop('selected_dep', None)
    if selected_dep is not None:
        dh_result = (
            DeviceHistory.objects.filter(parse_history=parse_history,
                                         device__department=DepartmentList.objects.get(name=selected_dep).pk)
                .values('device__fias__building_address', # выбираем AddressPoint
                        )
                .annotate(dh_count=Count('id')) # считаем количество записей DeviceHistory
        )
        d_result = (
            AddressPoint.objects.filter(department=DepartmentList.objects.get(name=selected_dep).pk)
                .values('department__name',
                        'building_address',
                        'lat',
                        'lon',
                        )
                .annotate(total_d_count=Count('device'))
        )
    else:
        dh_result = (
            DeviceHistory.objects.filter(parse_history=parse_history)
                .values('device__fias__building_address', # выбираем AddressPoint
                        )
                .annotate(dh_count=Count('id')) # считаем количество записей DeviceHistory
        )
        d_result = (
            AddressPoint.objects.all()
                .values('department__name',
                        'building_address',
                        'lat',
                        'lon',
                        )
                .annotate(total_d_count=Count('device'))
        )
    combined_data = {}
    for entry in d_result:
        ap_name = entry['building_address']
        total_devices = entry['total_d_count']
        matching_dh_entry = next((item for item in dh_result if item.get('device__fias__building_address') == ap_name),
                                 None)
        # Если нашли запись DeviceHistory, берём её значение, иначе устанавливаем 0
        history_count = matching_dh_entry['dh_count'] if matching_dh_entry else 0
        combined_data[ap_name] = {
            'department': entry['department__name'],
            'lat': entry['lat'],
            'lon': entry['lon'],
            'dh_count': history_count,
            'total_d_count': total_devices,
            'percentage': round(history_count / total_devices * 100, 2) if total_devices > 0 else 0
        }
    sorted_combined_data = sorted(combined_data.items(), key=lambda x: x[1]['percentage'], reverse=True)

    return sorted_combined_data


def group_by_percentage(sorted_combined_data, **kwargs):
    """ Функция возвращает словарь с числом записей DeviceHistory, сгруппированных по каждому AddressPoint для
    заданной записи ParseHistory, с общим числом ПУ на каждом AddressPoint, а так же их процентное соотношение"""
    info_type = kwargs.pop('info_type', None)
    groups = [
        {"range": "Опрос 0–20 %", "points": [], "color": 'red'},
        {"range": "Опрос 20–40 %", "points": [], "color": 'orange'},
        {"range": "Опрос 40–60 %", "points": [], "color": 'beige'},
        {"range": "Опрос 60–80 %", "points": [], "color": 'lightgreen'},
        {"range": "Опрос 80–100 %", "points": [], "color": 'green'}
    ]
    # Распределение по группам
    for addr_point, data in sorted_combined_data:
        percent = data["percentage"]
        if percent <= 20:
            groups[0]["points"].append((addr_point, data))
        elif percent <= 40:
            groups[1]["points"].append((addr_point, data))
        elif percent <= 60:
            groups[2]["points"].append((addr_point, data))
        elif percent <= 80:
            groups[3]["points"].append((addr_point, data))
        else:
            groups[4]["points"].append((addr_point, data))
    if info_type is not None:
        if info_type == 'range-count':
            groups_range_count = []
            for group in groups:
                groups_range_count.append(
                    {
                        'range': group["range"],
                        'count': len(group["points"]),
                    }
                )
            return groups_range_count
        else:
            return groups
    else:
        return groups
        # for group in group_by_percentage(all_points_stat):
        #     print(group["range"], len(group["points"]), "адресных точек")
        #     for point, data in group["points"]:
        #         print(" ", point, "-", f"{data['percentage']:.2f}%")


def get_count_by_address_point(**kwargs):
    selected_dep = kwargs.pop('selected_dep', None)
    if selected_dep is not None:
        points = AddressPoint.objects.filter(department__name=selected_dep).values('building_address','lat','lon').annotate(total_d_count=Count('device'))
    else:
        points = AddressPoint.objects.all().values('building_address', 'lat', 'lon').annotate(total_d_count=Count('device'))
    return points


def get_department_info(dep_list):
    dep_counts_info = []
    for dep_name in dep_list:
        dep_counts_info.append({
            'department': dep_name,
            'device_count': Device.objects.filter(department=dep_name).count(),
            'bs_count': BaseStation.objects.filter(department=dep_name).count(),
            'point_count': AddressPoint.objects.filter(department=dep_name).count()
        })
    return dep_counts_info


def get_department_bs_info(dep_list, last_bs_parses):
    dep_all_bs_history = []
    for dep_name in dep_list:
        dep_one_history = []
        for parse_record in last_bs_parses:
            count_devices = 0
            every_bs_for_dep = BaseStationHistory.objects.filter(basestation__department=dep_name,
                                                                 parse_history=parse_record)
            for every_bs in every_bs_for_dep:
                count_devices += every_bs.count_devices
            dep_one_history.append(count_devices)
        dep_all_bs_history.append({
            'department': dep_name,
            'device_counts': dep_one_history,
        })
    return dep_all_bs_history


def get_pu_parse_count(last_pu_parses, **kwargs):
    request_dep = kwargs.pop('request_dep', None)
    devices_parse_history = []
    if request_dep is None:
        for every_parse in last_pu_parses:
            parse_object = DeviceHistory.objects.filter(parse_history=every_parse).count()
            devices_parse_history.append(parse_object)
    else:
        for every_parse in last_pu_parses:
            parse_object = DeviceHistory.objects.filter(device__department=request_dep, parse_history=every_parse).count()
            devices_parse_history.append(parse_object)
    return devices_parse_history


def get_bs_last_parses(last_bs_parses):
    stations = BaseStation.objects.all().order_by('department__name',
                                                  'station_number')  # Берём все базовые станции
    stations_history = []
    for station in stations:
        station_one_history = []
        for parse_record in last_bs_parses:
            station_one_history.append(BaseStationHistory.objects.filter(basestation=station, parse_history=parse_record).first())
        stations_history.append({
            'station': station,
            'histories': station_one_history
        })
    return stations_history


def get_points_stat(last_pu_parses_d, **kwargs):
    request_dep = kwargs.pop('request_dep', None)
    last_points_stat = []
    if request_dep is not None:
        for parse in last_pu_parses_d:
            last_points_stat.append(
                {
                    'parse_object': parse,
                    'parse_points_info': get_count_devicehistory_by_address_point(parse, selected_dep=request_dep),
                }
            )
    else:
        for parse in last_pu_parses_d:
            last_points_stat.append(
                {
                    'parse_object': parse,
                    'parse_points_info': get_count_devicehistory_by_address_point(parse),
                }
            )
    for points_stat in last_points_stat:
        points_stat['parse_points_stat'] = group_by_percentage(points_stat['parse_points_info'],
                                                               info_type='range-count', )
        points_stat.pop('parse_points_info')
    return last_points_stat


def get_map_object(center_lat, center_lon, all_base_stations):
    m = folium.Map(location=[center_lat, center_lon],
                   zoom_start=12,
                   attributionControl=0, # убираем жовто-блакитную тряпку
                   tiles=None,
                   )
    osm_layer = folium.TileLayer(
        tiles='OpenStreetMap',
        name='Стандартная карта',
        overlay=False,  # Сделаем его активным по умолчанию
        control=True
    )
    arcgis_layer = folium.TileLayer(
                tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
                attr='Tiles © Esri — Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community',
                name='Спутниковая карта',
                overlay=False,
                show=False,
                control=True
    )
    osm_layer.add_to(m)
    arcgis_layer.add_to(m)
    folium.plugins.Fullscreen(
        position="topleft",
        title="Во весь экран",
        title_cancel="Свернуть",
        force_separate_button=True,
    ).add_to(m)
    folium.plugins.MousePosition(
        prefix="Координаты:",
    ).add_to(m)
    marker_cluster_bs = folium.FeatureGroup(name='Базовые станции', show=True)
    for base_station in all_base_stations:
        html_content_bs = """ <div style="display: inline-block;"><table class="popup-table" style='font-size: 12px; white-space: nowrap;'>
        <tr><td><strong>Адрес установки:</strong></td><td class='text-end'>{}</td></tr>
        <tr><td style='width:100px;'><strong>Номер базовой станции:</strong></td><td class='text-end'>{}</td></tr>
        </table></div>""".format(base_station.name, base_station.station_number)
        folium.Marker([base_station.lat, base_station.lon],
                      icon=folium.Icon(color='purple', icon='tower-cell', prefix='fa'),
                      zIndexOffset=1000,
                      popup=html_content_bs).add_to(marker_cluster_bs)
    marker_cluster_bs.add_to(m)
    return m


def map_generator(map_type, user_dep, **kwargs):
    last_parse_object = ParseHistory.objects.filter(parse_type__name='Опрос ПУ').last()
    if user_dep == 'Аппарат Управления':
        center_map = DepartmentList.objects.get(name='Тамбов')
        all_base_stations = BaseStation.objects.all()
        all_address_points_count = get_count_by_address_point()
        all_address_points_percentage = get_count_devicehistory_by_address_point(last_parse_object)
    elif DepartmentList.objects.filter(name=user_dep).exists():
        center_map = DepartmentList.objects.get(name=user_dep)
        all_base_stations = BaseStation.objects.filter(department__name=user_dep)
        all_address_points_count = get_count_by_address_point(selected_dep=user_dep)
        all_address_points_percentage = get_count_devicehistory_by_address_point(
            last_parse_object,
            selected_dep=user_dep,
        )
    else:
        center_map = DepartmentList.objects.get(name='Тамбов')
        all_base_stations = []
        all_address_points_count = []
        all_address_points_percentage = []
    m = get_map_object(center_map.lat, center_map.lon, all_base_stations)
    if map_type == 'count_on_point_map':
        marker_cluster_points = MarkerCluster(maxClusterRadius=50,
                                              disableClusteringAtZoom=14,
                                              name='Адреса установки ПУ',)
        for address_point in all_address_points_count:
            html_content = """ <div style="display: inline-block;"><table class="popup-table" style='font-size: 12px; white-space: nowrap;'>
            <tr><td><strong>Адрес:</strong></td><td class='text-end'>{}</td></tr>
            <tr><td style='width:100px;'><strong>Установлено:</strong></td><td class='text-end'>{} ПУ</td></tr>
            </table></div>""".format(address_point['building_address'], address_point['total_d_count'])
            folium.Marker([address_point['lat'], address_point['lon']],
                          icon=folium.Icon(color='blue', icon='microchip', prefix='fa'),
                          zIndexOffset=-1000,
                          popup=html_content).add_to(marker_cluster_points)
        marker_cluster_points.add_to(m)
        if user_dep == 'Аппарат Управления':
            map_description = 'На карте отображены адреса установки и количество ПУ по всему ТОСК'
        else:
            map_description = f'На карте отображены адреса установки и количество ПУ по подразделению {user_dep}'
    elif map_type == 'heatmap_map':
        point_groups = group_by_percentage(all_address_points_percentage)
        for group in point_groups:
            marker_cluster_points = MarkerCluster(maxClusterRadius=50,
                                                  disableClusteringAtZoom=14,
                                                  name=f'{group["range"]} ({len(group["points"])} адресных точек)',
                                                  )
            for point, data in group["points"]:
                html_content = """ <div style="display: inline-block;"><table class="popup-table" style='font-size: 12px; white-space: nowrap;'>
                <tr><td><strong>Адрес:</strong></td><td class='text-end'>{}</td></tr>
                <tr><td style='width:100px;'><strong>Обновили данные:</strong></td><td class='text-end'>{} ПУ</td></tr>
                <tr><td style='width:100px;'><strong>Установлено:</strong></td><td class='text-end'>{} ПУ</td></tr>
                <tr><td style='width:100px;'><strong>Процент опроса:</strong></td><td class='text-end'>{} %</td></tr>
                </table></div>""".format(point, data['dh_count'], data['total_d_count'], data['percentage'])
                folium.Marker([data['lat'], data['lon']],
                              icon=folium.Icon(color=group["color"], icon='microchip', prefix='fa'),
                              zIndexOffset=-1000,
                              popup=html_content).add_to(marker_cluster_points)
            marker_cluster_points.add_to(m)
        if user_dep == 'Аппарат Управления':
            map_description = f'На карте отображены группы адресов по проценту последнего опроса {last_parse_object.parse_end_time.astimezone().strftime('%d.%m.%Y г. %H:%M')} по всему ТОСК'
        else:
            map_description = f'На карте отображены группы адресов по проценту последнего опроса {last_parse_object.parse_end_time.astimezone().strftime('%d.%m.%Y г. %H:%M')} по подразделению {user_dep}'
    else:
        map_description = ''
    folium.LayerControl(collapsed=False).add_to(m)
    map_html = m._repr_html_()
    return {'map': map_html,
            'map_description': map_description,
            }


def get_xlsx_report(report_type, request_dep_num, parse_object, **kwargs):
    parse_history_obj = ParseHistory.objects.filter(pk=parse_object).last()
    pho_for_names = parse_history_obj.parse_end_time.strftime("%Y-%m-%d %H:%M")
    if request_dep_num != 0 and DepartmentList.objects.filter(pk=request_dep_num).exists():
        request_dep = DepartmentList.objects.get(pk=request_dep_num)
    else:
        request_dep = 'Аппарат управления'
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    workbook = Workbook()
    sheet = workbook.active
    table_rows = []
    table_headers = []
    dop_info = []
    file_name = 'имя файла'
    if report_type == 'pu-parse-all-address-points':
        sheet.title = 'Список адресов установки ПУ'
        table_headers = ['№', 'Группа опроса', 'Подразделение', 'Адрес', 'Количество установленных ПУ',
                         'Количество опрошенных ПУ', 'Процент опроса']
        if request_dep == 'Аппарат управления':
            file_name = f"Список адресов установки ПУ по проценту опроса по всему ТОСК за {pho_for_names}.xlsx"
            all_address_points_data = get_count_devicehistory_by_address_point(parse_history_obj)
        else:
            file_name = f"Список адресов установки ПУ по проценту опроса по подразделению {request_dep} за {pho_for_names}.xlsx"
            all_address_points_data = get_count_devicehistory_by_address_point(parse_history_obj, selected_dep=request_dep)
        for group in group_by_percentage(all_address_points_data):
            for i, (point, data) in enumerate(group["points"]):
                table_rows.append((i+1, group["range"], data['department'], point, data['total_d_count'], data['dh_count'], f'{data['percentage']}'))
    elif report_type == 'pu-parse-all-devices':
        sheet.title = 'Список приборов учета'
        table_headers = ['№', 'Подразделение', 'Адрес установки ПУ', 'Точный адрес установки ПУ',
                         'Номер ПУ', 'Опрошен в этот опрос', 'Показания', 'Время и дата записи данных с ПУ на сервер']
        if request_dep == 'Аппарат управления':
            file_name = f"Список приборов учета с результатом опроса по всему ТОСК за {pho_for_names}.xlsx"
            all_devices = Device.objects.all()
        else:
            file_name = f"Список приборов учета с результатом опроса по подразделению {request_dep} за {pho_for_names}.xlsx"
            all_devices = Device.objects.filter(department__name=request_dep)
        device_ids_with_records = DeviceHistory.objects.filter(
            parse_history=parse_history_obj
        ).values_list('device_id', flat=True)

        # Добавляем предварительную загрузку related objects
        all_devices = all_devices.prefetch_related(Prefetch(
            'devicehistory_set',
            queryset=DeviceHistory.objects.filter(parse_history=parse_history_obj),
            to_attr='relevant_histories'
        )).order_by('pk')

        count_devices_parsed = 0
        count_devices_fail = 0

        for i, device in enumerate(all_devices):
            has_history = device.pk in device_ids_with_records
            relevant_record = None
            if has_history and hasattr(device, 'relevant_histories'):
                # Берём первую подходящую запись из предзагруженного атрибута
                relevant_record = device.relevant_histories[0]
            meter_value = relevant_record.meter_value if relevant_record else "-"
            last_record_time = relevant_record.last_record_time.strftime(
                '%Y-%m-%d %H:%M:%S') if relevant_record else "-"
            table_rows.append((
                i+1,
                device.department.name,
                device.fias.building_address,
                device.address_1c,
                device.serial_number,
                'ДА' if has_history else 'НЕТ',
                meter_value,
                last_record_time,
            ))
            if has_history:
                count_devices_parsed += 1
            else:
                count_devices_fail += 1
        dop_info = ['Что подсчитано;Количество',
                    f'Всего ПУ;{len(all_devices)}',
                    f'ПУ с обновлением данных;{count_devices_parsed}',
                    f'ПУ без обновления данных;{count_devices_fail}',
                    ]
    sheet.append(table_headers)
    encoded_file_name = quote(file_name.encode('utf-8'))  # Кодируем имя файла
    response['Content-Disposition'] = f'attachment; filename*=UTF-8\'\'{encoded_file_name}'
    for row_data in table_rows:
        sheet.append(row_data)
    for add_info in dop_info:
        columns = add_info.split(';')
        sheet.append(columns)
    buffer = BytesIO()
    workbook.save(buffer)
    buffer.seek(0)
    response.write(buffer.read())
    return response


def get_coordinates_from_dadata(fias):
    token = settings.API_DADATA_TOKEN
    dadata = Dadata(token)
    result = dadata.find_by_id("address", fias)
    if result:
        return {'success': True,
                'lat': result[0]['data']['geo_lat'],
                'lon': result[0]['data']['geo_lon'],
                }
    else:
        return {'success': False,}


def is_strictly_numeric(s):
    return bool(re.fullmatch(r'\d+', s))


def file_upload_processing(file):
    unique_serial_numbers = set(Device.objects.values_list('serial_number', flat=True))
    unique_points = set(AddressPoint.objects.values_list('building_address', flat=True))
    unique_dep_check_list = {'Котовск', 'Тамбовск', 'Моршанск', 'Кирсановск', 'Мичуринск', 'Уваровск', 'Рассказовск', 'Жердевск'}
    pattern = '|'.join(unique_dep_check_list)
    compiled_pattern = re.compile(pattern, flags=re.I)
    clear_line_count = 0
    count_new_devices = 0
    count_old_devices = 0
    count_new_devices_fail = 0
    count_new_devices_fail_dep = 0
    count_new_points = 0
    possibly_new_devices = []
    result_file_rows = []
    try:
        for line in file:
            clear_line = line.decode('utf-8').strip()
            if 'ЗаводскойНомер' in clear_line:
                continue
            clear_line_count += 1
            row_serial_number = clear_line.partition(';')[0]
            if not is_strictly_numeric(row_serial_number):
                result_file_rows.append(f'{clear_line};Некорректный номер ПУ')
            elif row_serial_number in unique_serial_numbers:
                count_old_devices += 1
                result_file_rows.append(f'{clear_line};ПУ есть в системе')
            else:
                possibly_new_devices.append(clear_line)
        for row in possibly_new_devices:
            split_clear_line = row.split(';')
            if compiled_pattern.search(split_clear_line[6]):
                if split_clear_line[1] == '':
                    count_new_devices_fail += 1
                    result_file_rows.append(f'{row};У ПУ не указан Код ФИАС')
                else:
                    if split_clear_line[3] in unique_points:
                        device_address_point = AddressPoint.objects.get(building_address=split_clear_line[3])
                    else:
                        point_coordinates = get_coordinates_from_dadata(split_clear_line[1])
                        if point_coordinates['success']:
                            if 'Моршанск' in split_clear_line[6]:
                                depart_clear = DepartmentList.objects.get(name='Моршанск')
                            elif 'Тамбов' in split_clear_line[6]:
                                depart_clear = DepartmentList.objects.get(name='Тамбов')
                            elif 'Мичуринск' in split_clear_line[6]:
                                depart_clear = DepartmentList.objects.get(name='Мичуринск')
                            elif 'Кирсанов' in split_clear_line[6]:
                                depart_clear = DepartmentList.objects.get(name='Кирсанов')
                            elif 'Жердев' in split_clear_line[6]:
                                depart_clear = DepartmentList.objects.get(name='Жердевка')
                            elif 'Уваров' in split_clear_line[6]:
                                depart_clear = DepartmentList.objects.get(name='Уварово')
                            elif 'Рассказов' in split_clear_line[6]:
                                if not 'Рассказовский р-н' in split_clear_line[4]:
                                    depart_clear = DepartmentList.objects.get(name='Рассказово')
                                else:
                                    result_file_rows.append(f'{row};ПУ находится в специфичном подразделении')
                                    continue
                            elif 'Котовск' in split_clear_line[6]:
                                depart_clear = DepartmentList.objects.get(name='Котовск')
                            device_address_point = AddressPoint.objects.create(department=depart_clear,
                                                                               fias=split_clear_line[1],
                                                                               building_address=split_clear_line[3],
                                                                               lat=point_coordinates['lat'],
                                                                               lon=point_coordinates['lon'],)
                            unique_points.add(split_clear_line[3])
                            count_new_points += 1
                        else:
                            result_file_rows.append(f'{row};У ПУ указан Код ФИАС, но по нему не найдены координаты')
                            count_new_devices_fail += 1
                            continue
                    new_device = Device.objects.create(department=device_address_point.department,
                                                       serial_number=split_clear_line[0],
                                                       variety=split_clear_line[5],
                                                       fias=device_address_point,
                                                       address_1c=split_clear_line[4],)
                    result_file_rows.append(f'{row};ПУ добавлен в систему')
                    count_new_devices += 1
            else:
                count_new_devices_fail_dep += 1
                result_file_rows.append(f'{row};ПУ находится в специфичном подразделении')
        workbook = Workbook()
        sheet = workbook.active
        sheet.title = 'Результат загрузки'
        table_headers = ['ЗаводскойНомер', 'КодФИАС', 'ПодразделениеРодитель', 'СтроениеАдрес', 'ВладелецАдрес',
                         'ТипПрибораУчетаПоМестуУстановки', 'Подразделение', 'Результат загрузки']
        sheet.append(table_headers)
        for row_data in result_file_rows:
            columns = row_data.split(';')  # Разделение строки по ";"
            # Добавление данных в лист
            sheet.append(columns)
        dop_info = ['Что подсчитано;Количество',
                    f'ПУ в файле;{clear_line_count}',
                    f'ПУ уже в системе;{count_old_devices}',
                    f'Новых ПУ, добавленных в систему;{count_new_devices}',
                    f'Новых ПУ, НЕ добавленных в систему;{count_new_devices_fail}',
                    f'ПУ, в специфичном подразделении;{count_new_devices_fail_dep}',
                    f'Новых точек установки;{count_new_points}',
                    ]
        for add_info in dop_info:
            columns = add_info.split(';')  # Разделение строки по ";"
            # Добавление данных в лист
            sheet.append(columns)
        current_time = datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
        filename = f'Отчет_загрузки_приборов_учета_{current_time}.xlsx'
        file_path = os.path.join(settings.MEDIA_ROOT, 'upload_devices_reports', filename)

        workbook.save(file_path)

        return {'result': True,
                'filename': filename,
                }
    except Exception as e:
        print(e)
        return {'result': False,
                }


def list_upload_devices_reports():
    directory = os.path.join(settings.MEDIA_ROOT, 'upload_devices_reports')

    if not os.path.exists(directory):
        return []

    files_with_dates = [(file_name, os.path.getmtime(os.path.join(directory, file_name))) for file_name in
                        os.listdir(directory)]

    # Сортируем файлы по дате изменения (от новых к старым)
    sorted_files = sorted(files_with_dates, key=lambda x: x[1], reverse=True)

    # Возвращаем только имена файлов
    return [file_name for file_name, _ in sorted_files]