# REFERENCES
# Title: Simple Ecommerce
# Author: overiq
# Date Published: Dec 8, 2018
# Date Accessed: Oct 18, 2020
# Code version: commit 704596f
# URL: https://github.com/overiq/simple_ecommerce
# Software License: MIT License

from django.db import models
from taggit.managers import TaggableManager
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.conf import settings
from django.utils import timezone
from address.models import AddressField

# Create your models here.

class UserManager(BaseUserManager):
    def _create_user(self, email, password, is_staff, is_superuser, **kwargs):
        if not email:
            raise ValueError('Email is required for registration')
        now = timezone.now()
        email = self.normalize_email(email)
        user = self.model(
                email=email,
                is_active=True,
                is_staff=is_staff,
                is_superuser=is_superuser,
                date_joined=now,
        )
        user.set_password(password)
        user.save()
        return user

    def create_user(self, email, password, **kwargs):
        return self._create_user(email, password, False, False, **kwargs)

    def create_superuser(self, email, password, **kwargs):
        return self._create_user(email, password, True, True, **kwargs)

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=127, unique=True)
    first_name = models.CharField(max_length=127)
    last_name = models.CharField(max_length=127)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    # charities = models.ManyToManyField(CharityOrg)

    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def get_absolute_url(self):
        return "/users/%i" % (self.pk)

class CharityOrg(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField()
    # photo = models.ImageField()
    contact_email = models.EmailField()
    paypal_email = models.EmailField()
    slug = models.SlugField(unique=False, max_length=50)
    tags = TaggableManager()
    is_deleted = models.BooleanField(default=False)
    authenticated_users = models.ManyToManyField(User)
    charity_image = models.FileField(upload_to='images/', null=True, verbose_name="", default="http://127.0.0.1:8000/media/https:/i.pinimg.com/originals/fa/98/67/fa9867a39c2ec093bad63e91fed2bacb.jpg")


    def __str__(self):
        return self.name

class Cause(models.Model):
    name = models.CharField(max_length=50) # 191 is max SQL length
    description = models.TextField()
    charity = models.ForeignKey(CharityOrg, on_delete=models.CASCADE)
    slug = models.SlugField(unique=False, max_length=50)
    tags = TaggableManager()
    cause_image = models.ImageField(upload_to='images/', default="https://i.pinimg.com/originals/fa/98/67/fa9867a39c2ec093bad63e91fed2bacb.jpg")
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return "{}:{}".format(self.charity.name, self.name)

class CartItem(models.Model):
    cart_id = models.CharField(max_length=50)
    value = models.DecimalField(max_digits=7, decimal_places=2)
    cause = models.ForeignKey(Cause, on_delete=models.CASCADE)

    def __str__(self):
        return "{}:{}".format(self.cause.name, self.id)

    def update_value(self, newValue):
        self.value = newValue
        self.save()

class Order(models.Model):
    address = AddressField()
    contact_email = models.EmailField()
    date = models.DateTimeField(auto_now_add=True)
    paid = models.BooleanField(default=False)
    order_id = models.CharField(max_length=50)
    charities = models.ManyToManyField(CharityOrg, related_name='charity_orders')

    def __str__(self):
        return "{}:{}".format(self.id, self.contact_email)

    def total_cost(self):
        return sum([ l.value for l in self.lineitem_set.all() ])
    
    def charity_cost(self, charity):
        relevant_lineitems = []
        for l in self.lineitem_set.all():
            if l.cause.charity == charity:
                relevant_lineitems.append(l)
        return sum([ l.value for l in relevant_lineitems])


class LineItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    value = models.DecimalField(max_digits=7, decimal_places=2)
    cause = models.ForeignKey(Cause, on_delete=models.CASCADE)

    def __str__(self):
        return "{}:{}:{}".format(self.charity.name, self.cause.name, self.id)
