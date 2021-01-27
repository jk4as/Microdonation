# Generated by Django 3.1.3 on 2020-11-22 23:10

import address.models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import taggit.managers


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('address', '0003_auto_20200830_1851'),
        ('auth', '0012_alter_user_first_name_max_length'),
        ('taggit', '0003_taggeditem_add_unique_index'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('email', models.EmailField(max_length=127, unique=True)),
                ('first_name', models.CharField(max_length=127)),
                ('last_name', models.CharField(max_length=127)),
                ('is_staff', models.BooleanField(default=False)),
                ('is_superuser', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=True)),
                ('date_joined', models.DateTimeField(auto_now_add=True)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Cause',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=191)),
                ('description', models.TextField()),
                ('slug', models.SlugField()),
                ('cause_image', models.ImageField(default='https://i.pinimg.com/originals/fa/98/67/fa9867a39c2ec093bad63e91fed2bacb.jpg', upload_to='images/')),
                ('is_deleted', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='CharityOrg',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=191)),
                ('description', models.TextField()),
                ('contact_email', models.EmailField(max_length=254)),
                ('paypal_email', models.EmailField(max_length=254)),
                ('slug', models.SlugField()),
                ('is_deleted', models.BooleanField(default=False)),
                ('charity_image', models.FileField(default='http://127.0.0.1:8000/media/https:/i.pinimg.com/originals/fa/98/67/fa9867a39c2ec093bad63e91fed2bacb.jpg', null=True, upload_to='images/', verbose_name='')),
                ('authenticated_users', models.ManyToManyField(to=settings.AUTH_USER_MODEL)),
                ('tags', taggit.managers.TaggableManager(help_text='A comma-separated list of tags.', through='taggit.TaggedItem', to='taggit.Tag', verbose_name='Tags')),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('contact_email', models.EmailField(max_length=254)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('paid', models.BooleanField(default=False)),
                ('order_id', models.CharField(max_length=50)),
                ('address', address.models.AddressField(on_delete=django.db.models.deletion.CASCADE, to='address.address')),
                ('charities', models.ManyToManyField(related_name='charity_orders', to='microDonation.CharityOrg')),
            ],
        ),
        migrations.CreateModel(
            name='LineItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.DecimalField(decimal_places=2, max_digits=7)),
                ('cause', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='microDonation.cause')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='microDonation.order')),
            ],
        ),
        migrations.AddField(
            model_name='cause',
            name='charity',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='microDonation.charityorg'),
        ),
        migrations.AddField(
            model_name='cause',
            name='tags',
            field=taggit.managers.TaggableManager(help_text='A comma-separated list of tags.', through='taggit.TaggedItem', to='taggit.Tag', verbose_name='Tags'),
        ),
        migrations.CreateModel(
            name='CartItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cart_id', models.CharField(max_length=50)),
                ('value', models.DecimalField(decimal_places=2, max_digits=7)),
                ('cause', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='microDonation.cause')),
            ],
        ),
    ]