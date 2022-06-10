from django.db import models
from django.urls import reverse
from django.contrib.auth.models import (
    AbstractBaseUser, PermissionsMixin,
    BaseUserManager,
)
from cables_shop.settings import DELIVERY_PRICE
from phonenumber_field.modelfields import PhoneNumberField


class CableType(models.Model):
    """
    Model representing  cable types.
    plural name, description and photo renders on index page
    """
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
    def photo_url(self) -> str:
        """Get photo URL or empty string"""
        return self.photo.url if self.photo else ''


class Cable(models.Model):
    """Model representing  cable (products in this store)"""
    name = models.CharField('название', max_length=50)
    slug = models.SlugField('URL')
    length_sm = models.PositiveSmallIntegerField('длина, см.', default=0)
    price = models.PositiveIntegerField('цена, руб.', default=0)
    units_in_stock = models.PositiveSmallIntegerField('количество в наличии')
    is_for_sale = models.BooleanField('в продаже', default=True)
    description = models.TextField('описание', blank=True, null=True)
    type = models.ForeignKey(CableType, verbose_name='тип кабеля', on_delete=models.PROTECT)

    class Meta:
        verbose_name = 'кабель'
        verbose_name_plural = 'кабели'
        ordering = ('type', 'price')

    def __str__(self):
        return f'{self.name}, {self.length_sm} см.'

    def get_absolute_url(self):
        return reverse('cable_page', kwargs={'cable_slug': self.slug})

    @property
    def title_photo_url(self) -> str:
        """Get photo URL or empty string"""
        try:
            return self.cablephoto_set.get(is_title=True).photo_url
        except CablePhoto.DoesNotExist:
            return ''


class CablePhoto(models.Model):
    """
    Model representing photos for cables.
    Title photo is the one displayed on cable card on all cables page
    """
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
    def photo_url(self) -> str:
        """Get photo URL or empty string"""
        return self.photo.url if self.photo else ''


class CustomUserManager(BaseUserManager):
    """
    Overriding default user creation methods to add phone_number field
    and authenticate by email
    """
    def _create_user(
            self, email, password, first_name, last_name, phone_number, **extra_fields
    ):
        if not email:
            raise ValueError('Email is required')
        if not password:
            raise ValueError('Password is required')
        if not phone_number:
            raise ValueError('Phone number is required')

        user = self.model(
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(
            self, email, password, first_name, last_name, phone_number, **extra_fields
    ):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(
            email, password, first_name, last_name, phone_number, **extra_fields
        )

    def create_superuser(
            self, email, password, first_name, last_name, phone_number, **extra_fields
    ):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(
            email, password, first_name, last_name, phone_number, **extra_fields
        )


class User(AbstractBaseUser, PermissionsMixin):
    """ Overriding default user model """
    email = models.EmailField('email', max_length=70, unique=True)
    first_name = models.CharField('имя', max_length=50)
    last_name = models.CharField('фамилия', max_length=50)
    phone_number = PhoneNumberField('номер телефона', region='RU', unique=True)

    is_staff = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('first_name', 'last_name', 'phone_number')

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'пользователи'

    def __str__(self):
        return f'{self.email}'


class ShippingAddress(models.Model):
    customer = models.ForeignKey(
        User, on_delete=models.CASCADE,
        verbose_name='покупатель'
    )
    address = models.CharField('адрес', max_length=200, null=True)
    city = models.CharField('город', max_length=50, null=True)
    state = models.CharField('область', max_length=70, null=True)
    zipcode = models.CharField('почтовый индекс', max_length=10, null=True)

    class Meta:
        verbose_name = 'адрес доставки'
        verbose_name_plural = 'адреса доставки'

    def __str__(self):
        return f'Адрес покупателя {self.customer}, {self.zipcode}'


class Order(models.Model):
    class OrderStatus(models.TextChoices):
        IN_CART = 'IC', 'В корзине'
        ACCEPTED = 'AC', 'Принят'
        COMPLETE = 'CO', 'Выполнен'

    class DeliveryType(models.TextChoices):
        PICK_UP = 'PU', 'Самовывоз'
        DELIVERY = 'DE', 'Доставка'

    customer = models.ForeignKey(
        User,
        verbose_name='покупатель',
        on_delete=models.CASCADE,
        null=True
    )
    shipping_address = models.ForeignKey(
        ShippingAddress,
        verbose_name='адресс доставки',
        on_delete=models.CASCADE,
        null=True
    )
    order_accepted_date = models.DateField(
        'дата оформления заказа',
        auto_now_add=True
    )
    status = models.CharField(
        'статус заказа',
        max_length=10,
        choices=OrderStatus.choices,
        default=OrderStatus.IN_CART
    )
    delivery_type = models.CharField(
        'способ получения',
        max_length=10,
        choices=DeliveryType.choices,
        default=DeliveryType.DELIVERY
    )

    class Meta:
        verbose_name = 'заказ'
        verbose_name_plural = 'заказы'

    def __str__(self):
        return f'№{self.pk}: {self.customer}, {self.get_status_display()}'

    def get_absolute_url(self):
        return reverse('order_info_page', kwargs={'order_pk': self.pk})

    @property
    def products_total_price(self) -> int:
        """Returns total price for all products in cart"""
        ordered_products = self.orderedproduct_set.all()
        products_price = sum(
            [product.total_price for product in ordered_products]
        )
        return products_price

    @property
    def order_total_price(self) -> int:
        if self.delivery_type == Order.DeliveryType.DELIVERY:
            return self.products_total_price + DELIVERY_PRICE
        return self.products_total_price

    @property
    def order_total_products(self) -> int:
        """Returns total amount of unique products in cart"""
        return len(self.orderedproduct_set.all())


class OrderedProduct(models.Model):
    order = models.ForeignKey(Order, verbose_name='заказ', on_delete=models.CASCADE)
    product = models.ForeignKey(Cable, verbose_name='товар', on_delete=models.CASCADE)
    quantity = models.SmallIntegerField('заказанное количество', default=0)
    date_added = models.DateTimeField('время добавления', auto_now_add=True)

    class Meta:
        verbose_name = 'заказанный товар'
        verbose_name_plural = 'заказанные товары'

    def __str__(self):
        return f'#{self.order.pk}, {self.product}'

    @property
    def total_price(self) -> int:
        """Return total price for this product"""
        return self.product.price*self.quantity
