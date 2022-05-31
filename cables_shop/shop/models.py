from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class CableType(models.Model):
    name = models.CharField('название (ед.ч)', max_length=30, unique=True)
    name_plural = models.CharField('название (мн.ч)', max_length=50)
    slug = models.SlugField('URL')
    description = models.TextField('описание', blank=True, null=True)
    photo = models.ImageField(
        'фото',
        upload_to='photos/cable_types/',
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = 'тип кабеля'
        verbose_name_plural = 'типы кабелей'
        ordering = ('pk',)

    def __str__(self):
        return self.name

    @property
    def get_photo_url(self) -> str:
        """Get photo URL or empty string"""
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

    @property
    def get_title_photo_url(self) -> str:
        """Get photo URL or empty string"""
        try:
            title_photo_url = self.cablephoto_set.get(is_title=True).photo.url
        except ValueError:
            title_photo_url = ''

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
    def get_photo_url(self) -> str:
        """Get photo URL or empty string"""
        try:
            photo_url = self.photo.url
        except ValueError:
            photo_url = ''

        return photo_url


class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, unique=True, verbose_name='пользователь')
    first_name = models.CharField('имя', max_length=15)
    last_name = models.CharField('фамилия', max_length=15)
    phone = models.CharField('номер телефона', max_length=15)

    class Meta:
        verbose_name = 'клиент'
        verbose_name_plural = 'клиенты'

    def __str__(self):
        return self.user.username


@receiver(post_save, sender=User)
def create_customer_profile(sender, instance, created, **kwargs):
    if created:
        Customer.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_customer_profile(sender, instance, **kwargs):
    instance.customer.save()


class ShippingAddress(models.Model):
    customer = models.OneToOneField(Customer, on_delete=models.CASCADE, related_name='shipping_address', verbose_name='покупатель')
    address = models.CharField('адрес', max_length=200, null=True)
    city = models.CharField('город', max_length=50, null=True)
    state = models.CharField('область', max_length=70, null=True)
    zipcode = models.CharField('почтовый индекс', max_length=10, null=True)


class Order(models.Model):
    customer = models.ForeignKey(Customer, verbose_name='покупатель', on_delete=models.CASCADE)
    order_date = models.DateTimeField('дата заказа', auto_now_add=True)
    is_active = models.BooleanField('в процессе оформления', default=True)

    class Meta:
        verbose_name = 'заказ'
        verbose_name_plural = 'заказы'

    def __str__(self):
        return f'#{self.pk} {self.customer}, {"active" if self.is_active else "ordered"}'

    def get_cart_total_price(self) -> int:
        """Returns total price for all products in cart"""
        ordered_products = self.orderedproduct_set.all()
        return sum([product.get_product_total_price for product in ordered_products])

    def get_cart_total_products(self) -> int:
        """Returns total amount of unique products in cart"""
        return len(self.orderedproduct_set.all())


class OrderedProduct(models.Model):
    order = models.ForeignKey(Order, verbose_name='заказ', on_delete=models.CASCADE)
    product = models.ForeignKey(Cable, verbose_name='товар', on_delete=models.CASCADE)
    quantity = models.SmallIntegerField('количество', default=0)
    date_added = models.DateTimeField('время добавления', auto_now_add=True)

    class Meta:
        verbose_name = 'заказанный товар'
        verbose_name_plural = 'заказанные товары'

    def __str__(self):
        return f'#{self.order.pk}, {self.product}'

    @property
    def get_product_total_price(self) -> int:
        """Return total price for this product"""
        return self.product.price * self.quantity
