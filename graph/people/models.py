from django.db import models
from django.utils.translation import ugettext_lazy as _


class BaseNote(models.Model):
    TYPE_PUBLIC = 1
    TYPE_PRIVATE = 2
    TYPES = (
        (TYPE_PUBLIC, _('Public note')),
        (TYPE_PRIVATE, _('Private note'))
    )

    text = models.TextField()
    type = models.IntegerField(choices=TYPES)
    date_created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey('auth.User', null=True, on_delete=models.SET_NULL, related_name='+')

    def __str__(self):
        return f'#{self.id}: {self.text} at {self.date_created.date()}'

    class Meta:
        abstract = True


class Relationship(models.Model):
    first_person = models.ForeignKey('people.Person', related_name='+', on_delete=models.CASCADE)
    second_person = models.ForeignKey('people.Person', related_name='+', on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.first_person} <-> {self.second_person}'


class RelationshipStatusNote(BaseNote):
    REASON_STATUS_START = 1
    REASON_STATUS_END = 2
    REASON_OTHER = 3
    REASONS = (
        (REASON_STATUS_START, _('Note on relationship start')),
        (REASON_STATUS_END, _('Note on relationship end')),
        (REASON_OTHER, _('Unspecified reason'))
    )

    reason = models.IntegerField(choices=REASONS)
    status = models.ForeignKey('people.RelationshipStatus', related_name='notes', on_delete=models.CASCADE)


class RelationshipStatus(models.Model):
    STATUS_BLOOD_RELATIVE = 1
    STATUS_SIBLING = 2
    STATUS_PARENT_CHILD = 3
    STATUS_MARRIED = 4
    STATUS_ENGAGED = 5
    STATUS_DATING = 6
    STATUS_RUMOUR = 7

    STATUS_CHOICES = (
        (STATUS_BLOOD_RELATIVE, _('Blood relatives')),
        (STATUS_SIBLING, _('Siblings')),
        (STATUS_PARENT_CHILD, _('Parent-child')),
        (STATUS_MARRIED, _('Married')),
        (STATUS_ENGAGED, _('Engaged')),
        (STATUS_DATING, _('Dating')),
        (STATUS_RUMOUR, _('Rumour')),
    )

    relationship = models.ForeignKey('people.Relationship', related_name='statuses', on_delete=models.CASCADE)
    status = models.IntegerField(choices=STATUS_CHOICES)

    date_start = models.DateField(null=True, blank=True)
    date_end = models.DateField(null=True, blank=True)

    def __str__(self):
        return f'{self.relationship} {self.get_status_display()}'

    class Meta:
        verbose_name_plural = "relationship statuses"
        get_latest_by = ('date_end', 'date_start')


class PersonNote(BaseNote):
    person = models.ForeignKey('people.Person', related_name='notes', on_delete=models.CASCADE)


class Person(models.Model):
    GENDER_MALE = 1
    GENDER_FEMALE = 2
    GENDER_OTHER = 3

    GENDERS = (
        (GENDER_MALE, _('Male')),
        (GENDER_FEMALE, _('Female')),
        (GENDER_OTHER, _('Other'))
    )

    first_name = models.CharField(max_length=128)
    last_name = models.CharField(max_length=128)
    maiden_name = models.CharField(max_length=128, blank=True, null=True)

    nickname = models.CharField(max_length=128, null=True, blank=True)

    gender = models.IntegerField(choices=GENDERS)

    birth_date = models.DateField(null=True, blank=True)
    death_date = models.DateField(null=True, blank=True)

    visible = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.nickname or (self.first_name + self.last_name)}'

    class Meta:
        verbose_name_plural = "people"
        unique_together = ('first_name', 'last_name', 'nickname')


class Group(models.Model):
    CATEGORY_ELEMENTARY_SCHOOL = 1
    CATEGORY_HIGH_SCHOOL = 2
    CATEGORY_UNIVERSITY = 3
    CATEGORY_SEMINAR = 4
    CATEGORY_OTHER = 5

    CATEGORIES = (
        (CATEGORY_ELEMENTARY_SCHOOL, _('Elementary school')),
        (CATEGORY_HIGH_SCHOOL, _('High school')),
        (CATEGORY_UNIVERSITY, _('University school')),
        (CATEGORY_SEMINAR, _('Seminar')),
        (CATEGORY_OTHER, _('Other'))
    )

    category = models.IntegerField(choices=CATEGORIES)

    parent = models.ForeignKey('people.Group', null=True, blank=True, related_name='children', on_delete=models.SET_NULL)
    name = models.CharField(max_length=256, unique=True)

    visible = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.name}'


class GroupMembershipNote(BaseNote):
    membership = models.ForeignKey('people.GroupMembership', related_name='notes', on_delete=models.CASCADE)


class GroupMembership(models.Model):
    person = models.ForeignKey('people.Person', related_name='memberships', on_delete=models.CASCADE)
    group = models.ForeignKey('people.Group', related_name='memberships', on_delete=models.CASCADE)

    date_started = models.DateField(null=True, blank=True)
    date_ended = models.DateField(null=True, blank=True)

    class Meta:
        unique_together = ('person', 'group')
