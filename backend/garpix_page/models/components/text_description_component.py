from django.db import models
from .base_component import BasePageComponent


class TextDescriptionPageComponent(BasePageComponent):
    text = models.TextField(verbose_name='Текст')
    description = models.TextField(verbose_name='Описание', blank=True, default='')
    template = 'garpix_page/components/text_description.html'

    class Meta:
        verbose_name = "Текст+описание"
        verbose_name_plural = "Текст+описание"
        ordering = ('-created_at',)
