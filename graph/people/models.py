from typing import List, Optional

from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from django.db.models import Prefetch, Q, F, Exists, OuterRef, QuerySet, Case, When, Value
from django.db.models.functions import Coalesce
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from people.utils.variable_res_date import VariableResolutionDateField


class ExportableEnum:
    pass


class BaseNote(models.Model):
    class Types(models.IntegerChoices):
        PUBLIC = 1, _('Public note')
        PRIVATE = 2, _('Private note')

    text = models.TextField()
    type = models.IntegerField(choices=Types.choices)
    date_created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, related_name='+')

    def __str__(self):
        return f'#{self.id}: {self.text} at {self.date_created.date()}'

    class Meta:
        abstract = True


class RelationshipQuerySet(models.QuerySet):
    def get_or_create_for_people(self, person_1, person_2, defaults=None):
        try:
            return Relationship.objects.get(
                Q(first_person=person_1, second_person=person_2) | Q(second_person=person_1, first_person=person_2)
            )
        except Relationship.DoesNotExist:
            defaults = defaults or {}
            return Relationship.objects.create(
                first_person=person_1,
                second_person=person_2,
                **defaults
            )

    def with_people(self):
        return self.select_related('first_person', 'second_person')

    def confirmed(self):
        return self.filter(
            Exists(RelationshipStatus.objects.filter(relationship=OuterRef('pk'),
                                                     confirmed_by=RelationshipStatus.ConfirmationBy.BOTH))
        )

    def visible(self):
        return self.filter(first_person__visible=True, second_person__visible=True).filter(
            Exists(RelationshipStatus.objects.filter(relationship=OuterRef('pk'), visible=True))
        )

    def for_people(self, people):
        people_pks = people.values_list('pk', flat=True)
        return self.filter(
            Q(first_person__in=people_pks) | Q(second_person__in=people_pks)
        )

    def with_status_for_date(self, date=None):
        date = date or timezone.localdate()
        return self.prefetch_related(
            Prefetch(
                'statuses',
                queryset=RelationshipStatus.objects.for_date(date).order_by('relationship', '-date_start').distinct(
                    'relationship'),
                to_attr='current_status'
            )
        )

    def with_recent_statuses(self):
        return self.prefetch_related(
            Prefetch(
                'statuses',
                queryset=RelationshipStatus.objects.visible().confirmed().order_by('relationship', '-date_start'),
                to_attr='recent_statuses'
            )
        )

    def for_graph_serialization(self, people):
        return self.with_people().for_people(people).with_recent_statuses().visible().confirmed()


class Relationship(models.Model):
    first_person = models.ForeignKey('people.Person', related_name='relationships_as_first', on_delete=models.CASCADE)
    second_person = models.ForeignKey('people.Person', related_name='relationships_as_second', on_delete=models.CASCADE)

    objects = RelationshipQuerySet.as_manager()

    def __str__(self):
        return f'{self.first_person} & {self.second_person}'

    class Meta:
        unique_together = ('first_person', 'second_person')


class RelationshipStatusNote(BaseNote):
    class Reasons(models.IntegerChoices):
        STATUS_START = 1, _('Note on relationship start')
        STATUS_END = 2, _('Note on relationship end')
        OTHER = 3, _('Unspecified reason')

    reason = models.IntegerField(choices=Reasons.choices)
    status = models.ForeignKey('people.RelationshipStatus', related_name='notes', on_delete=models.CASCADE)


class RelationshipStatusQuerySet(models.QuerySet):
    def subquery_for_person(self):
        return self.filter(Q(relationship__first_person=OuterRef('pk')) | Q(relationship__second_person=OuterRef('pk')))

    def for_date(self, date):
        return self.filter(date_start__lte=date).exclude(date_end__lt=date)

    def current(self):
        return self.for_date(timezone.localdate())

    def romantic(self):
        return self.filter(
            Q(status=RelationshipStatus.StatusChoices.DATING) | Q(status=RelationshipStatus.StatusChoices.ENGAGED) | Q(
                status=RelationshipStatus.StatusChoices.MARRIED)
        )

    def with_duration(self):
        return self.annotate(
            duration=Coalesce(F('date_end'), timezone.localdate()) - F('date_start'),
        )

    def with_confirmation_status(self, pov_of: 'Person'):
        return self.annotate(
            confirmation_status=Case(
                When(Q(confirmed_by=RelationshipStatus.ConfirmationBy.BOTH),
                     then=Value('Confirmed by both people in the relationship')),
                When(Q(confirmed_by=RelationshipStatus.ConfirmationBy.NONE),
                     then=Value('Awaiting approval from both people in the relationship')),
                When(
                    (Q(relationship__first_person=pov_of) & Q(
                        confirmed_by=RelationshipStatus.ConfirmationBy.FIRST)) | (
                            Q(relationship__second_person=pov_of) & Q(
                        confirmed_by=RelationshipStatus.ConfirmationBy.SECOND)),
                    then=Value('Awaiting the confirmation of the other person')
                ),
                default=Value('Awaiting your confirmation')
            )
        )

    def visible(self):
        return self.filter(visible=True)

    def confirmed(self):
        return self.filter(confirmed_by=RelationshipStatus.ConfirmationBy.BOTH)


class RelationshipStatus(models.Model):
    class StatusChoices(ExportableEnum, models.IntegerChoices):
        BLOOD_RELATIVE = 1, _('Blood relatives')
        SIBLING = 2, _('Siblings')
        PARENT_CHILD = 3, _('Parent-child')
        MARRIED = 4, _('Married')
        ENGAGED = 5, _('Engaged')
        DATING = 6, _('Dating')
        RUMOUR = 7, _('Rumour')

    class ConfirmationBy(models.IntegerChoices):
        NONE = 0, _('Awaiting approval from both people in the relationship')
        FIRST = 1, _('Confirmed by the first person')
        SECOND = 2, _('Confirmed by the second person')
        BOTH = 3, _('Confirmed by both people')

    relationship = models.ForeignKey('people.Relationship', related_name='statuses', on_delete=models.CASCADE)
    status = models.IntegerField(choices=StatusChoices.choices)

    date_start = VariableResolutionDateField(null=True, blank=True)
    date_end = VariableResolutionDateField(null=True, blank=True)

    confirmed_by = models.IntegerField(choices=ConfirmationBy.choices, default=ConfirmationBy.NONE)
    visible = models.BooleanField(default=False)

    objects = RelationshipStatusQuerySet.as_manager()

    def __str__(self):
        return f'{self.relationship} - {self.get_status_display()}'

    class PersonPerspective:
        def __init__(self, status: 'RelationshipStatus', pov_of: 'Person', partner_of=False):
            self.status = status

            if pov_of == self.status.relationship.first_person:
                self.pov_of = self.status.relationship.first_person
                self.partner_pov = self.status.relationship.second_person
                self.pov_confirmation_mask = RelationshipStatus.ConfirmationBy.FIRST
                self.partner_confirmation_mask = RelationshipStatus.ConfirmationBy.SECOND
            else:
                self.pov_of = self.status.relationship.second_person
                self.partner_pov = self.status.relationship.first_person
                self.pov_confirmation_mask = RelationshipStatus.ConfirmationBy.SECOND
                self.partner_confirmation_mask = RelationshipStatus.ConfirmationBy.FIRST

            if partner_of:
                self.pov_of, self.partner_pov = self.partner_pov, self.pov_of
                self.pov_confirmation_mask, self.partner_confirmation_mask = self.partner_confirmation_mask, self.pov_confirmation_mask

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            pass

        @property
        def confirmed_by_me(self):
            return self.status.confirmed_by & self.pov_confirmation_mask > 0

        @property
        def confirmed_by_partner(self):
            return self.status.confirmed_by & self.partner_confirmation_mask > 0

        def set_confirmed_for_me(self, flag):
            if flag:
                self.status.confirmed_by |= self.pov_confirmation_mask
            else:
                self.status.confirmed_by &= self.partner_confirmation_mask

        def set_confirmed_for_partner(self, flag):
            if flag:
                self.status.confirmed_by |= self.partner_confirmation_mask
            else:
                self.status.confirmed_by &= self.pov_confirmation_mask

    class Meta:
        verbose_name_plural = "relationship statuses"
        get_latest_by = ('date_end', 'date_start')
        ordering = ('-date_start',)


class PersonNote(BaseNote):
    person = models.ForeignKey('people.Person', related_name='notes', on_delete=models.CASCADE)


class PersonManager(UserManager):
    pass


class PersonQuerySet(models.QuerySet):
    def with_current_relationships(self):
        qs = self.prefetch_related(Prefetch(
            'relationships_as_first',
            queryset=Relationship.objects.with_status_for_date(),
            to_attr='current_relationships_1'
        )).prefetch_related(Prefetch(
            'relationships_as_second',
            queryset=Relationship.objects.with_status_for_date(),
            to_attr='current_relationships_2'
        ))
        return qs

    def single(self):
        return self.exclude(Exists(RelationshipStatus.objects.subquery_for_person().romantic().current()))

    def in_romantic_relationship(self):
        return self.filter(Exists(RelationshipStatus.objects.subquery_for_person().romantic().current()))

    def female(self):
        return self.filter(gender=Person.Genders.FEMALE)

    def male(self):
        return self.filter(gender=Person.Genders.MALE)

    def has_relationship_status(self, statuses: List[int]):
        return self.filter(
            Exists(RelationshipStatus.objects.subquery_for_person().current().filter(status__in=statuses)))

    def in_age_range(self, age_years_from: Optional[int] = None, age_years_to: Optional[int] = None) -> QuerySet:
        qs = self
        if age_years_from:
            qs = qs.filter(birth_date__lte=timezone.localdate() - relativedelta(years=age_years_from))
        if age_years_to:
            qs = qs.filter(birth_date__gte=timezone.localdate() - relativedelta(years=age_years_to))
        return qs

    def with_visible_memberships(self):
        return self.prefetch_related(
            Prefetch(
                'memberships',
                queryset=GroupMembership.objects.filter(visible=True),
                to_attr='visible_memberships'
            )
        )

    def for_graph_serialization(self):
        return self.filter(visible=True).with_visible_memberships().order_by('pk')


class Person(AbstractUser):
    class Genders(ExportableEnum, models.IntegerChoices):
        MALE = 1, _('Male')
        FEMALE = 2, _('Female')
        OTHER = 3, _('Other')

    maiden_name = models.CharField(max_length=128, blank=True, null=True)

    nickname = models.CharField(max_length=128, null=True, blank=True)

    gender = models.IntegerField(choices=Genders.choices, default=Genders.OTHER)

    birth_date = VariableResolutionDateField(null=True, blank=True)
    death_date = VariableResolutionDateField(null=True, blank=True)

    visible = models.BooleanField(default=False)

    objects = PersonManager()
    qs = PersonQuerySet.as_manager()

    @property
    def name(self):
        return f'{self.first_name} {self.last_name}'

    def __str__(self):
        if self.first_name and self.last_name:
            return self.name
        if self.nickname:
            return self.nickname
        return super().__str__()

    class Meta:
        verbose_name = "person"
        verbose_name_plural = "people"
        unique_together = ('first_name', 'last_name', 'nickname')
        ordering = ('-birth_date',)


class ManagementAuthority(models.Model):
    manager = models.ForeignKey('people.Person', on_delete=models.CASCADE, related_name='subjects')
    subject = models.ForeignKey('people.Person', on_delete=models.CASCADE, related_name='managers')

    def __str__(self):
        return f'{self.subject} managed by {self.manager}'


class Group(models.Model):
    class Categories(ExportableEnum, models.IntegerChoices):
        ELEMENTARY_SCHOOL = 1, _('Elementary school')
        HIGH_SCHOOL = 2, _('High school')
        UNIVERSITY = 3, _('University')
        SEMINAR = 4, _('Seminar')
        OTHER = 5, _('Other')

    category = models.IntegerField(choices=Categories.choices)

    parent = models.ForeignKey('people.Group', null=True, blank=True, related_name='children',
                               on_delete=models.SET_NULL)
    name = models.CharField(max_length=256, unique=True)

    def __str__(self):
        return f'{self.name}'

    class Meta:
        ordering = ('name',)


class GroupMembershipNote(BaseNote):
    membership = models.ForeignKey('people.GroupMembership', related_name='notes', on_delete=models.CASCADE)


class GroupMembershipQuerySet(models.QuerySet):
    def with_duration(self):
        return self.annotate(
            duration=Coalesce(F('date_ended'), timezone.localdate()) - Coalesce(F('date_started'),
                                                                                timezone.localdate()),
        )


class GroupMembership(models.Model):
    person = models.ForeignKey('people.Person', related_name='memberships', on_delete=models.CASCADE)
    group = models.ForeignKey('people.Group', related_name='memberships', on_delete=models.CASCADE)

    date_started = VariableResolutionDateField(null=True, blank=True)
    date_ended = VariableResolutionDateField(null=True, blank=True)

    visible = models.BooleanField(default=False)

    objects = GroupMembershipQuerySet.as_manager()

    class Meta:
        unique_together = ('person', 'group')
        ordering = ('-date_started',)
