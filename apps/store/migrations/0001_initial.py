# Generated by Django 3.1.3 on 2021-02-23 04:25

import cloudinary.models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import django_countries.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Card',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('src_id', models.CharField(max_length=30)),
                ('line1', models.CharField(max_length=30)),
                ('line2', models.CharField(blank=True, max_length=30, null=True)),
                ('city', models.CharField(max_length=30)),
                ('state', models.CharField(max_length=30)),
                ('zipcode', models.CharField(max_length=20)),
                ('country', django_countries.fields.CountryField(max_length=2)),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(default='Guest', max_length=100)),
                ('email', models.EmailField(blank=True, max_length=50, null=True)),
                ('stripe_customer_id', models.CharField(blank=True, max_length=100, null=True)),
                ('purchase_attempt_time', models.DateTimeField(blank=True, null=True)),
                ('guest_num', models.IntegerField(blank=True, default=0, null=True)),
                ('user', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='FilterCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='FilterName',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30, unique=True)),
                ('filter_category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='store.filtercategory')),
            ],
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
                ('description', models.TextField()),
                ('price', models.FloatField(default=0)),
                ('discount_price', models.FloatField(blank=True, null=True)),
                ('quantity', models.IntegerField(default=0)),
                ('image', cloudinary.models.CloudinaryField(blank=True, max_length=255, null=True)),
                ('slug', models.SlugField(blank=True, null=True, unique=True)),
                ('is_active', models.BooleanField(default=True)),
                ('total_sold', models.IntegerField(default=0)),
                ('total_earnings', models.IntegerField(default=0)),
                ('daily_earnings', models.IntegerField(default=0)),
                ('weekly_earnings', models.IntegerField(default=0)),
                ('monthly_earnings', models.IntegerField(default=0)),
                ('yearly_earnings', models.IntegerField(default=0)),
                ('filter_name', models.ManyToManyField(blank=True, to='store.FilterName')),
            ],
        ),
        migrations.CreateModel(
            name='ItemCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30, unique=True)),
                ('slug', models.SlugField(blank=True, unique=True)),
                ('date_started', models.DateTimeField(default=django.utils.timezone.now)),
                ('is_active', models.BooleanField(default=True)),
                ('total_earnings', models.IntegerField(default=0)),
                ('daily_earnings', models.IntegerField(default=0)),
                ('weekly_earnings', models.IntegerField(default=0)),
                ('monthly_earnings', models.IntegerField(default=0)),
                ('yearly_earnings', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(blank=True, max_length=100, null=True)),
                ('email', models.CharField(blank=True, max_length=30, null=True)),
                ('payment_intent_id', models.CharField(blank=True, max_length=30, null=True)),
                ('ref_code', models.CharField(blank=True, max_length=20, null=True)),
                ('date', models.DateTimeField(blank=True, null=True)),
                ('ordered', models.BooleanField(default=False)),
                ('delivered', models.BooleanField(default=False)),
                ('recieved', models.BooleanField(default=False)),
                ('refund_requested', models.BooleanField(default=False)),
                ('refund_granted', models.BooleanField(default=False)),
                ('cancelled', models.BooleanField(default=False)),
                ('card', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='store.card')),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='store.customer')),
            ],
        ),
        migrations.CreateModel(
            name='ShippingAddress',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('line1', models.CharField(max_length=30)),
                ('line2', models.CharField(blank=True, max_length=30, null=True)),
                ('city', models.CharField(max_length=30)),
                ('state', models.CharField(max_length=30)),
                ('zipcode', models.CharField(max_length=30)),
                ('country', django_countries.fields.CountryField(max_length=2)),
                ('first_name', models.CharField(max_length=30)),
                ('last_name', models.CharField(max_length=30)),
                ('email', models.EmailField(max_length=30)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='store.customer')),
            ],
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField(default=0)),
                ('in_cart', models.BooleanField(default=False)),
                ('ordered', models.BooleanField(default=False)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='store.customer')),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='store.item', verbose_name='Item List')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='store.order')),
            ],
        ),
        migrations.AddField(
            model_name='order',
            name='shipping_address',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='shipping_address', to='store.shippingaddress'),
        ),
        migrations.AddField(
            model_name='item',
            name='item_category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='store.itemcategory'),
        ),
        migrations.AddField(
            model_name='filtercategory',
            name='item_category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='store.itemcategory'),
        ),
        migrations.AddField(
            model_name='card',
            name='customer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='store.customer'),
        ),
    ]
