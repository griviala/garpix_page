from django.utils.functional import cached_property
from django.db import models
from django.utils import translation
from django.conf import settings
from django.urls import reverse
from django.contrib.sites.models import Site
from django.contrib.sites.managers import CurrentSiteManager
from garpix_page.utils.get_file_path import get_file_path
from polymorphic_tree.models import PolymorphicMPTTModel, PolymorphicTreeForeignKey, PolymorphicMPTTModelManager


class GCurrentSiteManager(CurrentSiteManager):
    use_in_migrations = False


def get_all_sites():
    return Site.objects.all()


class BaseComponent(PolymorphicMPTTModel):
    """
    Базовый компонент, на основе которой создаются все прочие компоненты.
    """
    title = models.CharField(max_length=255, verbose_name='Название')
    is_active = models.BooleanField(default=True, verbose_name='Включено')
    sites = models.ManyToManyField(Site, default=get_all_sites, verbose_name='Сайты для отображения')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата изменения')

    # objects = models.Manager()
    objects = PolymorphicMPTTModelManager()
    on_site = GCurrentSiteManager()

    template = 'garpix_page/components/default.html'
    searchable_fields = ('title',)
    serializer = None  # default is generator of serializers: garpix_page.serializers.serializer.get_serializer

    class Meta(PolymorphicMPTTModel.Meta):
        verbose_name = 'Структура компонентов'
        verbose_name_plural = 'Структура компонентов'
        ordering = ('created_at', 'title',)

    def __str__(self):
        return self.title

    def get_verbose_model_name(self):
        return self._meta.verbose_name

    get_verbose_model_name.short_description = 'Название модели'

    def get_absolute_url(self):
        return self.absolute_url
    get_absolute_url.short_description = 'URL'

    def get_absolute_url_html(self):
        return f'<a href="{self.absolute_url}" target="_blank">{self.absolute_url}</a>'
    get_absolute_url_html.short_description = 'URL'
    get_absolute_url_html.allow_tags = True

    @cached_property
    def get_sites(self):
        res = 'n/a'
        if self.sites.all().count() > 0:
            res = ''
            for site in self.sites.all():
                res += f'{site.domain} '
        return res

    get_sites.short_description = 'Sites'

    def get_template(self):
        return self.template

    def get_context(self, request=None, *args, **kwargs):
        context = {
            'request': request,
            'object': self,
        }
        return context

    @classmethod
    def is_for_page_view(cls):
        return True

    def get_breadcrumbs(self):
        result = []
        obj = self
        result.append(obj)
        while obj.parent is not None:
            result.insert(0, obj.parent)
            obj = obj.parent
        return result

    def get_admin_url_edit_object(self):
        url = reverse(f'admin:{self._meta.app_label}_{self._meta.model_name}_change', args=[self.id])
        return url

    def get_serializer(self):
        return self.serializer

    def model_name(self):
        return self.get_real_instance_class()._meta.verbose_name  # noqa
    model_name.short_description = 'Тип'
