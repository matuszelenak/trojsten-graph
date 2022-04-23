import random
import string

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class ContentUpdateRequest(models.Model):
    class Statuses(models.IntegerChoices):
        REQUEST = 1, _('Request')
        ACCEPTED = 2, _('Accepted')
        REJECTED = 3, _('Rejected')

    submitted_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='content_update_requests', on_delete=models.SET_NULL, null=True, verbose_name=_('submitted by'))
    status = models.IntegerField(choices=Statuses.choices, default=Statuses.REQUEST, verbose_name=_('status'))
    content = models.TextField(verbose_name=_('content'))

    date_created = models.DateTimeField(auto_now_add=True, verbose_name=_('date created'))
    date_resolved = models.DateTimeField(null=True, blank=True, verbose_name=_('date resolved'))

    def __str__(self):
        return f'{self.submitted_by}: {self.content[:100]}'


class InviteCodeQuerySet(models.QuerySet):
    def bulk_generate(self, number=1):
        return self.bulk_create([self.model(code=''.join(random.sample(string.ascii_uppercase, 10))) for _ in range(number)])


class InviteCode(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='invite_code', on_delete=models.CASCADE, null=True, blank=True, verbose_name=_('user'))
    code = models.CharField(max_length=10, unique=True, verbose_name=_('code'))

    objects = InviteCodeQuerySet.as_manager()

    def __str__(self):
        return f'{self.code} {self.user or ""}'


class EmailPatternWhitelist(models.Model):
    pattern = models.CharField(max_length=256, verbose_name=_('pattern'))

    def __str__(self):
        return f'Pattern {self.pattern}'


class Token(models.Model):
    class Types(models.IntegerChoices):
        ACCOUNT_ACTIVATION = 1, _('Account activation')
        PASSWORD_RESET = 2, _('Password reset')
        AUTH = 3, _('Auth token')
        EMAIL_CHANGE = 4, _('Email change')

    type = models.IntegerField(choices=Types.choices, default=Types.ACCOUNT_ACTIVATION, verbose_name=_('type'))
    token = models.CharField(max_length=50, verbose_name=_('token'))
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='token', on_delete=models.CASCADE, verbose_name=_('user'))
    valid = models.BooleanField(default=True, verbose_name=_('valid'))
    date_created = models.DateTimeField(auto_now_add=True, verbose_name=_('date created'))

    extra_data = models.JSONField(default=dict)

    @staticmethod
    def get_random_token():
        return ''.join(random.sample(string.ascii_uppercase + string.ascii_lowercase + string.digits, 50))

    @classmethod
    def create_for_user(cls, user, token_type=Types.ACCOUNT_ACTIVATION):
        return cls(
            token=cls.get_random_token(),
            user=user,
            type=token_type
        )

    def __str__(self):
        return f'{self.get_type_display()} token {self.token} for {self.user}'

    class Meta:
        unique_together = ('type', 'token')
