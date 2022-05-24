from django.db import models


class CableType(models.Model):
    name = models.CharField('Название (ед.ч)', max_length=30, unique=True)
    name_plural = models.CharField('Название (мн.ч)', max_length=50)
    slug = models.SlugField('URL')
    description = models.TextField('Описание', blank=True, null=True)
    photo = models.ImageField('Фото', upload_to='photos/cable_types/', blank=True, null=True)

    class Meta:
        verbose_name = 'Тип кабеля'
        verbose_name_plural = 'Типы кабелей'
        ordering = ('pk',)

    def __str__(self):
        return f'#{self.pk} {self.name}'
