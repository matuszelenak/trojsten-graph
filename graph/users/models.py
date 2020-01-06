import random
import string

from django.db import models


class ContentSuggestion(models.Model):
    class Statuses(models.IntegerChoices):
        REQUEST = 1, 'Request'
        ACCEPTED = 2, 'Accepted'
        REJECTED = 3, 'Rejected'

    submitted_by = models.ForeignKey('auth.User', related_name='content_suggestions', on_delete=models.SET_NULL, null=True)
    status = models.IntegerField(choices=Statuses.choices, default=Statuses.REQUEST)
    suggestion = models.TextField()

    date_created = models.DateTimeField(auto_now_add=True)
    date_resolved = models.DateTimeField(null=True, blank=True)


class InviteCodeQuerySet(models.QuerySet):
    def bulk_generate(self, number=1):
        return self.bulk_create([self.model(code=''.join(random.sample(string.ascii_uppercase, 10))) for _ in range(number)])


class InviteCode(models.Model):
    user = models.OneToOneField('auth.User', related_name='invite_code', on_delete=models.CASCADE, null=True, blank=True)
    code = models.CharField(max_length=10, unique=True)

    objects = InviteCodeQuerySet.as_manager()


class EmailPatternWhitelist(models.Model):
    pattern = models.CharField(max_length=256)


class Token(models.Model):
    class Types(models.IntegerChoices):
        ACCOUNT_ACTIVATION = 1, 'Account activation'
        PASSWORD_RESET = 2, 'Password reset'

    type = models.IntegerField(choices=Types.choices, default=Types.ACCOUNT_ACTIVATION)
    token = models.CharField(max_length=50)
    user = models.ForeignKey('auth.User', related_name='token', on_delete=models.CASCADE)
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
