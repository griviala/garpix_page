from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.functional import cached_property
from django.db import models
from django.urls import reverse
from django.contrib.sites.models import Site
from django.contrib.sites.managers import CurrentSiteManager
from rest_framework.views import APIView

from garpix_page.utils.get_current_language_code_url_prefix import get_current_language_code_url_prefix
from garpix_page.utils.get_file_path import get_file_path
from polymorphic_tree.models import PolymorphicMPTTModel, PolymorphicTreeForeignKey, PolymorphicMPTTModelManager
from django.utils.html import format_html


class GCurrentSiteManager(CurrentSiteManager):
    use_in_migrations = False


class GPolymorphicCurrentSiteManager(CurrentSiteManager, PolymorphicMPTTModelManager):
    use_in_migrations = False

    def get_queryset(self):
        qs = self.queryset_class(self.model, using=self._db, hints=self._hints)
        if self.model._meta.proxy:
            qs = qs.instance_of(self.model)
        return qs.filter(**{self._get_field_name() + '__id': settings.SITE_ID})


def get_all_sites():
    return Site.objects.all()


class BasePage(PolymorphicMPTTModel):
    """
    Базовая страница, на основе которой создаются все прочие страницы.
    """
    title = models.CharField(max_length=255, verbose_name='Название')
    is_active = models.BooleanField(default=True, verbose_name='Включено')
    display_on_sitemap = models.BooleanField(default=True, verbose_name='Отображать в карте сайта')
    slug = models.SlugField(max_length=150, verbose_name='ЧПУ', blank=True, default='')
    sites = models.ManyToManyField(Site, default=get_all_sites, verbose_name='Сайты для отображения')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата изменения')
    seo_title = models.CharField(max_length=250, verbose_name='SEO заголовок страницы (title)', blank=True, default='')
    seo_keywords = models.CharField(max_length=250, verbose_name='SEO ключевые слова (keywords)', blank=True,
                                    default='')
    seo_description = models.TextField(verbose_name='SEO описание (description)', blank=True, default='')
    seo_author = models.CharField(max_length=250, verbose_name='SEO автор (author)', blank=True, default='')
    seo_og_type = models.CharField(max_length=250, verbose_name='SEO og:type', blank=True, default="website")
    seo_image = models.FileField(upload_to=get_file_path, blank=True, null=True, verbose_name='SEO изображение')
    parent = PolymorphicTreeForeignKey('self', null=True, blank=True, related_name='children',
                                       db_index=True, verbose_name='Родительская страница', on_delete=models.SET_NULL,
                                       limit_choices_to={})

    # objects = models.Manager()
    objects = PolymorphicMPTTModelManager()
    on_site = GCurrentSiteManager()
    polymorphic_on_site = GPolymorphicCurrentSiteManager()

    template = 'garpix_page/default.html'
    searchable_fields = ('title',)
    serializer = None  # default is generator of serializers: garpix_page.serializers.serializer.get_serializer
    permissions = None

    class Meta(PolymorphicMPTTModel.Meta):
        verbose_name = 'Структура страниц'
        verbose_name_plural = 'Структура страниц'
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
    def absolute_url(self):
        current_language_code_url_prefix = get_current_language_code_url_prefix()

        if self.slug:
            obj = self
            url_arr = [self.slug]
            while obj.parent is not None:
                obj = obj.parent
                if obj.slug:
                    url_arr.insert(0, obj.slug)
            return "{}/{}".format(current_language_code_url_prefix, '/'.join(url_arr))
        return "{}".format(current_language_code_url_prefix) if len(current_language_code_url_prefix) > 1 else '/'

    absolute_url.short_description = 'URL'

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

    def has_permission_required(self, request):

        view = APIView()
        view.queryset = type(self).objects.filter(id=self.id)
        if self.permissions is not None:
            for permission in [permission() for permission in self.permissions]:
                if not permission.has_object_permission(request, view, self) or not permission.has_permission(request,
                                                                                                              view):
                    return False
        return True

    def clean(self):
        languages = [x[0] for x in settings.LANGUAGES]
        if BasePage.on_site.filter(slug=self.slug).exclude(pk=self.pk).exists():
            raise ValidationError({'slug': 'Страница с таким ЧПУ существует'})
        if self.slug in languages:
            raise ValidationError({'slug': f'ЧПУ не должен совпадать с языковым кодом ({languages})'})

    def get_components_context(self, request):
        context = []
        components = self.pagecomponent_set.filter(component__is_active=True)
        for component in components:
            component_context = {
                'view_order': component.view_order
            }
            component_context.update(component.component.get_context_data(request))
            context.append(component_context)
        return context

    def admin_link_to_add_component(self):
        link = reverse("admin:garpix_page_basecomponent_add")
        return format_html('<a class="related-widget-wrapper-link add-related addlink" href="{0}?_to_field=id&_popup=1&pages={1}">Добавить компонент</a>', link, self.id)
