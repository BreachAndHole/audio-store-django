from django.db import models
from django.urls import reverse


class CableType(models.Model):

    name = models.CharField('название (ед.ч)', max_length=30, unique=True)
    name_plural = models.CharField('название (мн.ч)', max_length=50)
    slug = models.SlugField('URL')
    description = models.TextField('описание', blank=True, null=True)
    photo = models.ImageField('фото', upload_to='photos/cable_types/', null=True, blank=True)

    class Meta:
        verbose_name = 'тип кабеля'
        verbose_name_plural = 'типы кабелей'
        ordering = ('pk',)

    def __str__(self):
        return self.name

    @property
    def get_photo_url(self):
        try:
            photo_url = self.photo.url
        except ValueError:
            photo_url = ''
        return photo_url


class Cable(models.Model):

    name = models.CharField('название', max_length=50)
    slug = models.SlugField('URL')
    length_sm = models.PositiveSmallIntegerField('длина, см.', default=0)
    price = models.PositiveIntegerField('цена, руб.', default=0)
    units_in_stock = models.PositiveSmallIntegerField('количество в наличии')
    description = models.TextField('описание', blank=True, null=True)
    type = models.ForeignKey(CableType, on_delete=models.PROTECT)

    class Meta:
        verbose_name = 'кабель'
        verbose_name_plural = 'кабели'
        ordering = ('type', 'price')

    def __str__(self):
        return f'#{self.pk} {self.name}'

    def get_absolute_url(self):
        return reverse('cable_page', kwargs={'cable_slug': self.slug})

    def get_title_photo_url(self):
        try:
            title_photo_url = self.cablephoto_set.get(is_title=True).photo.url
        except ValueError:
            title_photo_url = ''
        print(f'{title_photo_url = }')
        return title_photo_url


class CablePhoto(models.Model):

    photo = models.ImageField('фото', upload_to='photos/cable_photos/%Y/%m')
    cable = models.ForeignKey(Cable, verbose_name='кабель', on_delete=models.CASCADE)
    is_title = models.BooleanField('является титульным')

    class Meta:
        verbose_name = 'фото'
        verbose_name_plural = 'фотографии'
        ordering = ('pk', '-is_title')

    def __str__(self):
        return f'{"title " if self.is_title else ""}{self.cable.name[:5]}...'

    @property
    def get_photo_url(self):
        try:
            photo_url = self.photo.url
        except ValueError:
            photo_url = ''
        return photo_url
