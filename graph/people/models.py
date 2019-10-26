from django.db import models
from django.utils.translation import ugettext_lazy as _


class Note(models.Model):
    text = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey('auth.User', null=True, on_delete=models.SET_NULL, related_name='notes')

    def __str__(self):
        return f'#{self.id}: {self.text} at {self.date_created.date()}'


class Relationship(models.Model):
    first_person = models.ForeignKey('people.Person', related_name='+', on_delete=models.CASCADE)
    second_person = models.ForeignKey('people.Person', related_name='+', on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.first_person} <-> {self.second_person}'


class RelationshipStatus(models.Model):
    STATUS_BLOOD_RELATIVE = 1
    STATUS_SIBLING = 2
    STATUS_PARENT_CHILD = 3
    STATUS_MARRIED = 4
    STATUS_ENGAGED = 5
    STATUS_DATING = 6
    STATUS_RUMOUR = 7
    STATUS_OLD_RUMOUR = 8

    STATUS_CHOICES = (
        (STATUS_BLOOD_RELATIVE, _('Blood relatives')),
        (STATUS_SIBLING, _('Siblings')),
        (STATUS_PARENT_CHILD, _('Parent-child')),
        (STATUS_MARRIED, _('Married')),
        (STATUS_ENGAGED, _('Engaged')),
        (STATUS_DATING, _('Dating')),
        (STATUS_RUMOUR, _('Rumour')),
        (STATUS_OLD_RUMOUR, _('Old rumour')),
    )

    relationship = models.ForeignKey('people.Relationship', related_name='statuses', on_delete=models.CASCADE)
    status = models.IntegerField(choices=STATUS_CHOICES)

    date_start = models.DateField(null=True, blank=True)
    date_end = models.DateField(null=True, blank=True)

    notes = models.ManyToManyField('people.Note', related_name='relationship_notes')

    def __str__(self):
        return f'{self.relationship} {self.get_status_display()}'


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

    nickname = models.CharField(max_length=128, unique=True, null=True, blank=True)

    gender = models.IntegerField(choices=GENDERS)

    birth_date = models.DateField(null=True, blank=True)
    death_date = models.DateField(null=True, blank=True)

    visible = models.BooleanField(default=True)
    notes = models.ManyToManyField('people.Note', related_name='person_notes')

    def __str__(self):
        return f'{self.nickname or (self.first_name + self.last_name)}'


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
    name = models.CharField(max_length=256)

    visible = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.name}'


class GroupMembership(models.Model):
    person = models.ForeignKey('people.Person', related_name='memberships', on_delete=models.CASCADE)
    group = models.ForeignKey('people.Group', related_name='memberships', on_delete=models.CASCADE)

    date_started = models.DateField(null=True, blank=True)
    date_ended = models.DateField(null=True, blank=True)

    notes = models.ManyToManyField('people.Note', related_name='group_notes')
