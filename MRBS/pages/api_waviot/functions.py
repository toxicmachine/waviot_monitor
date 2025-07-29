import time

import requests
import datetime
import jwt
import pytz
from django.db.models import Max
from requests_oauth2client import BearerToken

from django.conf import settings

from ..models import *


def get_token():
    token_request = requests.post(url=settings.API_SERVER_NAME + 'auth',
                                  params={"login": settings.API_LOGIN,
                                          "password": settings.API_PASS})
    token = token_request.json()
    token_decoded_payload = jwt.decode(token['WAVIOT_JWT'], options={"verify_signature": False})
    token_expiration_time = token_decoded_payload['exp']
    return {'token': token,
            'expiration_time': token_expiration_time,
            }


# requests.get("http://192.168.1.250:8081/telecom/api/stinfo?bs_ids=13328", auth=BearerAuth(token['WAVIOT_JWT']))
def get_bs_info(comment_field):
    all_stations = BaseStation.objects.all()
    new_parse = ParseHistory(parse_type=ParseTemp.objects.get(name='Опрос БС'))
    new_parse.save()
    token = get_token()
    for station in all_stations:
        request_check = False
        while not request_check:
            try:
                current_time = int(datetime.datetime.now(datetime.UTC).timestamp())
                if token['expiration_time'] - 20 < current_time:
                    token = get_token()
                request_for_bs = requests.get(settings.API_SERVER_NAME + 'telecom/api/stinfo',
                                              auth=BearerToken(token['token']['WAVIOT_JWT']),
                                              params={'bs_ids': station.station_number,
                                                      },
                                              timeout=5)
                request_check = True
                BaseStationHistory(basestation=station,
                                   count_devices=request_for_bs.json()['BS_Total']['attached']['stations'][
                                       str(station.station_number)]['modems'],
                                   list_devices=request_for_bs.json()['BS_Total']['attached']['x_ids'],
                                   parse_history=new_parse).save()
            except Exception as e:
                continue
    new_parse.parse_comment = comment_field
    new_parse.save()
    return True


def chunked_queryset(queryset, chunk_size=500):
    """ Функция принимает QuerySet и размер чанка (группы), возвращая генератор, выдающий список объектов по указанным размерам. """
    start = 0
    while True:
        chunk = list(queryset[start:start + chunk_size])  # Используем срез QuerySet
        if not chunk:
            break
        yield chunk
        start += chunk_size


def round_if_float(value):
    """Округляет значение до целого, если оно имеет тип float."""
    return round(value) if isinstance(value, float) else value


def get_pu_info_extended(comment_field, **kwargs):
    all_devices = Device.objects.all()
    last_parse_object = ParseHistory.objects.filter(parse_type__name='Опрос ПУ').last()
    new_parse = ParseHistory(parse_type=ParseTemp.objects.get(name='Опрос ПУ'))
    new_parse.save()
    token = get_token()
    # правильная идея
    # опрашиваю суточные
    for i, devices_chunk in enumerate(chunked_queryset(all_devices, chunk_size=300)):
        serial_numbers_str = ','.join([device.serial_number for device in devices_chunk])
        request_check = False
        while not request_check:
            try:
                current_time = int(datetime.datetime.now(datetime.UTC).timestamp())
                if token['expiration_time'] - 20 < current_time:
                    token = get_token()
                request_for_pu = requests.get(settings.API_SERVER_NAME + 'driver_electro5/api/report/history',
                                              auth=BearerToken(token['token']['WAVIOT_JWT']),
                                              params={'modem': serial_numbers_str,
                                                      'profile': '1.0.98.2.0.255',
                                                      },
                                              timeout=3
                                              )
                request_check = True
                for element in request_for_pu.json():
                    last_parse_record = DeviceHistory.objects.filter(device=Device.objects.get(serial_number=element['modem'])).order_by('-last_record_time').last()
                    if element['meterings']:
                        # проверка, что последняя запись на waviot не совпадает с имеющейся
                        new_last_record_time = datetime.datetime.fromtimestamp(element['meterings'][0]['ts_get'], tz=pytz.timezone(settings.TIME_ZONE))
                        if last_parse_record is not None:
                            if not last_parse_record.last_record_time < new_last_record_time:
                                continue
                            else:
                                DeviceTempHistory(device=Device.objects.get(serial_number=element['modem']),
                                                  last_record_time=new_last_record_time,
                                                  meter_value=round_if_float(element['meterings'][0]['1.8.0']) / 1000,
                                                  parse_history=new_parse).save()
                        else:
                            DeviceTempHistory(device=Device.objects.get(serial_number=element['modem']),
                                              last_record_time=new_last_record_time,
                                              meter_value=round_if_float(element['meterings'][0]['1.8.0']) / 1000,
                                              parse_history=new_parse).save()
            except Exception as e:
                continue
    # получаю те ПУ, по которым не получил суточные
    devices_without_history = Device.objects.exclude(devicetemphistory__isnull=False)
    # опрашиваю часовые
    for i, devices_chunk in enumerate(chunked_queryset(devices_without_history, chunk_size=25)):
        serial_numbers_str = ','.join([device.serial_number for device in devices_chunk])
        request_check = False
        while not request_check:
            try:
                current_time = int(datetime.datetime.now(datetime.UTC).timestamp())
                if token['expiration_time'] - 20 < current_time:
                    token = get_token()
                request_for_pu = requests.get(settings.API_SERVER_NAME + 'driver_electro5/api/report/history',
                                              auth=BearerToken(token['token']['WAVIOT_JWT']),
                                              params={'modem': serial_numbers_str,
                                                      'profile': '1.0.99.1.0.255',
                                                      },
                                              timeout=5
                                              )
                request_check = True
                for element in request_for_pu.json():
                    last_parse_record = DeviceHistory.objects.filter(device=Device.objects.get(serial_number=element['modem'])).order_by('-last_record_time').last()
                    if element['meterings']:
                        # проверка, что последняя запись на waviot не совпадает с имеющейся
                        new_last_record_time = datetime.datetime.fromtimestamp(element['meterings'][0]['ts_get'], tz=pytz.timezone(settings.TIME_ZONE))
                        if last_parse_record is not None:
                            if not last_parse_record.last_record_time < new_last_record_time:
                                continue
                            else:
                                DeviceTempHistory(device=Device.objects.get(serial_number=element['modem']),
                                                  last_record_time=new_last_record_time,
                                                  meter_value=round_if_float(element['meterings'][0]['1.8.0']) / 1000,
                                                  parse_history=new_parse).save()
                        else:
                            DeviceTempHistory(device=Device.objects.get(serial_number=element['modem']),
                                              last_record_time=new_last_record_time,
                                              meter_value=round_if_float(element['meterings'][0]['1.8.0']) / 1000,
                                              parse_history=new_parse).save()
            except Exception as e:
                continue
    # получаю те ПУ, по которым нет показаний на локальном waviot
    devices_without_history = Device.objects.exclude(devicetemphistory__isnull=False)
    # запросу к облаку waviot
    for device in devices_without_history:
        request_check = False
        while not request_check:
            try:
                request_for_device = requests.get("https://lk.waviot.ru/api.data/get_modem_channel_values/",
                                                  params={'modem_id': hex(int(device.serial_number))[2:],
                                                          'channel': 'electro_ac_p_lsum_t1',
                                                          'key': settings.API_WCK,
                                                          'from': str(int(last_parse_object.parse_end_time.timestamp())),
                                                          'to': str(int(time.time())),
                                                          },
                                                  timeout=3
                                                  ).json()
                request_check = True
                if not request_for_device['status'] == 'ok':
                    continue
                else:
                    if request_for_device['values'] is None:
                        continue
                    else:
                        values_dict = request_for_device['values']
                        keys_list = list(values_dict.keys())  # получаем список ключей
                        first_key = keys_list[0]  # извлекаем первый ключ
                        value_for_first_key = values_dict[first_key]
                        last_parse_record = DeviceHistory.objects.filter(device=Device.objects.get(serial_number=device.serial_number)).order_by('-last_record_time').last()
                        new_last_record_time = datetime.datetime.fromtimestamp(int(first_key), tz=pytz.timezone(settings.TIME_ZONE))
                        if last_parse_record is not None:
                            if not last_parse_record.last_record_time < new_last_record_time:
                                continue
                            else:
                                DeviceTempHistory(device=Device.objects.get(serial_number=device.serial_number),
                                                  last_record_time=new_last_record_time,
                                                  meter_value=round_if_float(float(value_for_first_key)) / 1000,
                                                  parse_history=new_parse).save()
                        else:
                            DeviceTempHistory(device=Device.objects.get(serial_number=device.serial_number),
                                              last_record_time=new_last_record_time,
                                              meter_value=round_if_float(float(value_for_first_key)) / 1000,
                                              parse_history=new_parse).save()
            except Exception as e:
                continue
    for record in DeviceTempHistory.objects.all():
        new_instance = DeviceHistory(
            device=record.device,
            last_record_time=record.last_record_time,
            meter_value=record.meter_value,
            parse_history=new_parse,
        )
        new_instance.save()
    DeviceTempHistory.objects.all().delete()
    new_parse.parse_comment = comment_field
    new_parse.save()
    return True
