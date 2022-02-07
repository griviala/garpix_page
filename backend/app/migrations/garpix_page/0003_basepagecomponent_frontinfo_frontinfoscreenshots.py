# Generated by Django 3.1 on 2022-02-07 22:09

from django.db import migrations, models
import django.db.models.deletion
import garpix_utils.file.file_field
import polymorphic_tree.models


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('garpix_page', '0002_auto_20210908_0926'),
    ]

    operations = [
        migrations.CreateModel(
            name='FrontInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(max_length=128, verbose_name='Тип')),
                ('short_description', models.TextField(verbose_name='Краткое описание')),
                ('description', models.TextField(verbose_name='Полное описание')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Дата изменения')),
            ],
            options={
                'verbose_name': 'Информация для фронта',
                'verbose_name_plural': 'Информация для фронта',
                'ordering': ('created_at',),
            },
        ),
        migrations.CreateModel(
            name='FrontInfoScreenshots',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('screenshot', models.ImageField(upload_to=garpix_utils.file.file_field.get_file_path, verbose_name='Скриншот')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Дата изменения')),
                ('front_info', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='front_info_screenshots', to='garpix_page.frontinfo', verbose_name='Информация для фронта')),
            ],
            options={
                'verbose_name': 'Скриншот информации для фронта',
                'verbose_name_plural': 'Скриншоты информации для фронта',
                'ordering': ('front_info', 'created_at'),
            },
        ),
        migrations.CreateModel(
            name='BasePageComponent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, verbose_name='Название')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Дата изменения')),
                ('text_title', models.CharField(blank=True, default='', max_length=128, verbose_name='Заголовок')),
                ('lft', models.PositiveIntegerField(editable=False)),
                ('rght', models.PositiveIntegerField(editable=False)),
                ('tree_id', models.PositiveIntegerField(db_index=True, editable=False)),
                ('level', models.PositiveIntegerField(editable=False)),
                ('front_info', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='garpix_page.frontinfo', verbose_name='Информация для фронта')),
                ('pages', models.ManyToManyField(blank=True, related_name='components', to='garpix_page.BasePage', verbose_name='Страницы для отображения')),
                ('parent', polymorphic_tree.models.PolymorphicTreeForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='children', to='garpix_page.basepagecomponent', verbose_name='Родительский компонент')),
                ('polymorphic_ctype', models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='polymorphic_garpix_page.basepagecomponent_set+', to='contenttypes.contenttype')),
            ],
            options={
                'verbose_name': 'Компонент',
                'verbose_name_plural': 'Компоненты',
                'ordering': ('created_at', 'title'),
                'abstract': False,
                'base_manager_name': 'objects',
            },
        ),
    ]
