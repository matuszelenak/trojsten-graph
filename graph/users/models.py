import random
import string

from django.conf import settings
from django.db import models


class ContentUpdateRequest(models.Model):
    class Statuses(models.IntegerChoices):
        REQUEST = 1, 'Request'
        ACCEPTED = 2, 'Accepted'
        REJECTED = 3, 'Rejected'

    submitted_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='content_update_requests', on_delete=models.SET_NULL, null=True)
    status = models.IntegerField(choices=Statuses.choices, default=Statuses.REQUEST)
    content = models.TextField()

    date_created = models.DateTimeField(auto_now_add=True)
    date_resolved = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f'{self.submitted_by}: {self.content[:100]}'


class InviteCodeQuerySet(models.QuerySet):
    def bulk_generate(self, number=1):
        return self.bulk_create([self.model(code=''.join(random.sample(string.ascii_uppercase, 10))) for _ in range(number)])


class InviteCode(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='invite_code', on_delete=models.CASCADE, null=True, blank=True)
    code = models.CharField(max_length=10, unique=True)

    objects = InviteCodeQuerySet.as_manager()

    def __str__(self):
        return f'{self.code} {self.user or ""}'


class EmailPatternWhitelist(models.Model):
    pattern = models.CharField(max_length=256)

    def __str__(self):
        return f'Pattern {self.pattern}'


class Token(models.Model):
    class Types(models.IntegerChoices):
        ACCOUNT_ACTIVATION = 1, 'Account activation'
        PASSWORD_RESET = 2, 'Password reset'

    type = models.IntegerField(choices=Types.choices, default=Types.ACCOUNT_ACTIVATION)
    token = models.CharField(max_length=50)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='token', on_delete=models.CASCADE)
    valid = models.BooleanField(default=True)
    date_created = models.DateTimeField(auto_now_add=True)

    @staticmethod
    def get_random_token():
        return ''.join(random.sample(string.ascii_uppercase + string.ascii_lowercase + string.digits, 50))

    @classmethod
    def create_for_user(cls, user):
        return cls(
            token=cls.get_random_token(),
            user=user,
        )

    def __str__(self):
        return f'{self.get_type_display()} token {self.token} for {self.user}'
