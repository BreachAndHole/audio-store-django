from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User


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


class CablePhoto(models.Model):
    photo = models.ImageField('фото', upload_to='photos/cable_photos/%Y/%m')
    cable = models.ForeignKey(Cable, verbose_name='кабель', on_delete=models.CASCADE)
    is_title = models.BooleanField('является титульным')

    class Meta:
        verbose_name = 'фото'
        verbose_name_plural = 'фотографии'
        ordering = ('pk', '-is_title')

    def __str__(self):
        return f'Фото#{self.pk}, {"title " if self.is_title else ""}{self.cable.name[:5]}...'

    @property
    def get_photo_url(self):
        try:
            photo_url = self.photo.url
        except ValueError:
            photo_url = ''
        return photo_url


class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, blank=True, null=True)
    first_name = models.CharField(max_length=30, null=True)
    last_name = models.CharField(max_length=30, null=True)
    middle_name = models.CharField(max_length=30, null=True, blank=True)
    email = models.EmailField(null=True)
    phone = models.CharField(max_length=15, null=True, blank=True, unique=True)

    def __str__(self):
        return self.first_name


class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    order_date = models.DateTimeField(auto_now_add=True)
    is_made = models.BooleanField(default=False)
    transaction_id = models.CharField(max_length=20, null=True)

    def __str__(self):
        return str(self.pk)


class OrderedItem(models.Model):
    item = models.ForeignKey(Cable, on_delete=models.SET_NULL, null=True, blank=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.SmallIntegerField(default=0, null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.item


class ShippingAddress(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True)
    address = models.CharField(max_length=150, null=True, blank=True)
    city = models.CharField(max_length=50, null=True, blank=True)
    region = models.CharField(max_length=50, null=True, blank=True)
    zipcode = models.CharField(max_length=15, null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.address
