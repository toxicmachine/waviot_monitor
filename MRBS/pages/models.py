import datetime

from django.db import models
from django.utils import timezone


class DepartmentList(models.Model):
    name = models.CharField(max_length=100, verbose_name="Подразделение")
    # 52.721295, 41.452750
    lat = models.FloatField(default=52.721295)
    lon = models.FloatField(default=41.452750)

    def __str__(self):
        return self.name


class ParseTemp(models.Model):
    status = models.BooleanField(default=False)
    name = models.CharField(max_length=30, verbose_name="Вид опроса", default='Пустое имя')

    def __str__(self):
        return self.name


class ParseHistory(models.Model):
    parse_comment = models.CharField(max_length=150, verbose_name="Комментарий запуска", default='Опрос сервера')
    parse_type = models.ForeignKey(ParseTemp, on_delete=models.PROTECT)
    parse_start_time = models.DateTimeField(verbose_name='Дата и время начала опроса сервера', auto_now_add=True)
    parse_end_time = models.DateTimeField(verbose_name='Дата и время конца опроса сервера', auto_now=True)

    def __str__(self):
        return f"{self.parse_comment}-{self.parse_start_time}-{self.parse_end_time}"


class BaseStation(models.Model):
    class Meta:
        verbose_name = 'УСПД'
        verbose_name_plural = 'УСПД'

    department = models.ForeignKey(DepartmentList, on_delete=models.PROTECT)
    name = models.CharField(max_length=150, verbose_name="Адрес установки")
    station_number = models.CharField(max_length=20, verbose_name="Номер УСПД", unique=True, db_index=True)
    lat = models.FloatField()
    lon = models.FloatField()

    def __str__(self):
        return self.name


class BaseStationHistory(models.Model):
    class Meta:
        verbose_name = 'Запись о количестве ПУ через УСПД в этот день'
        verbose_name_plural = 'Записи о количестве ПУ через УСПД в разные дни'

    basestation = models.ForeignKey(BaseStation, on_delete=models.CASCADE, verbose_name='Номер УСПД')
    count_devices = models.PositiveBigIntegerField(verbose_name="Количество опрошенных ПУ")
    list_devices = models.JSONField(default=dict, verbose_name="Список ПУ")
    parse_history = models.ForeignKey(ParseHistory, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.basestation}-{self.parse_history}"


class AddressPoint(models.Model):
    class Meta:
        verbose_name = 'ФИАС'
        verbose_name_plural = 'ФИАС'

    department = models.ForeignKey(DepartmentList, on_delete=models.PROTECT)
    fias = models.CharField(max_length=80, verbose_name="Код ФИАС", blank=True, null=True, db_index=True)
    building_address = models.CharField(max_length=250, verbose_name="Адрес строения", db_index=True)
    lat = models.FloatField(blank=True, null=True,)
    lon = models.FloatField(blank=True, null=True,)

    def __str__(self):
        return self.building_address


class Device(models.Model):
    class Meta:
        verbose_name = 'Прибор учета'
        verbose_name_plural = 'Приборы учета'

    department = models.ForeignKey(DepartmentList, on_delete=models.PROTECT)
    serial_number = models.CharField(max_length=20, verbose_name="Заводской номер ПУ", unique=True, db_index=True)
    variety = models.CharField(max_length=40, verbose_name="Тип прибора учета")
    fias = models.ForeignKey(AddressPoint, on_delete=models.PROTECT, verbose_name='Код ФИАС')
    address_1c = models.CharField(max_length=250, verbose_name="Адрес установки ПУ", db_index=True)
    adding_date = models.DateField(verbose_name='Дата добавления ПУ', default=datetime.date.today)

    def __str__(self):
        return self.serial_number


class DeviceHistory(models.Model):
    class Meta:
        verbose_name = 'Запись опроса прибора учета'
        verbose_name_plural = 'Записи опроса приборов учета'

    device = models.ForeignKey(Device, on_delete=models.CASCADE, verbose_name='Заводской номер ПУ')
    # basestation = models.ForeignKey(BaseStation, on_delete=models.DO_NOTHING, verbose_name='Номер УСПД') # нет толкового api
    last_record_time = models.DateTimeField(verbose_name='Время и дата записи данных с ПУ на сервер', null=True)
    meter_value = models.FloatField(verbose_name='Показания ПУ', null=True)
    parse_history = models.ForeignKey(ParseHistory, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.device}-{self.parse_history}"


class DeviceTempHistory(models.Model):
    class Meta:
        verbose_name = 'Запись опроса прибора учета'
        verbose_name_plural = 'Записи опроса приборов учета'

    device = models.ForeignKey(Device, on_delete=models.CASCADE, verbose_name='Заводской номер ПУ')
    # basestation = models.ForeignKey(BaseStation, on_delete=models.DO_NOTHING, verbose_name='Номер УСПД') # нет толкового api
    last_record_time = models.DateTimeField(verbose_name='Время и дата записи данных с ПУ на сервер', null=True)
    meter_value = models.FloatField(verbose_name='Показания ПУ', null=True)
    parse_history = models.ForeignKey(ParseHistory, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.device}-{self.parse_history}"


class ChangeHistory(models.Model):
    class Meta:
        verbose_name = 'Изменение'
        verbose_name_plural = 'Изменения'

    version = models.CharField(max_length=20, verbose_name="Номер версии", unique=True)
    description = models.TextField(verbose_name="Описание изменений")

    def __str__(self):
        return self.version

