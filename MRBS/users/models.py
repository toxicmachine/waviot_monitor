from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    MultipleObjectsReturned = None
    DoesNotExist = None
    department = models.CharField(blank=True, null=True, max_length=100)
    email_notify = models.BooleanField(default=False, verbose_name='Уведомления на почту')

    def save(self, *args, **kwargs):
        if self.password and not self.pk:  # проверяем наличие первичного ключа (PK)
            self.set_password(self.password)  # применяем хеширование
        super().save(*args, **kwargs)
