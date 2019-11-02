from django.db import models
from django.db.models import Prefetch, Q, F
from django.db.models.functions import Coalesce
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from people.utils import snake_to_camel, random_token


class IntegerEnum(models.IntegerChoices):
    @classmethod
    def as_json(cls):
        return {
            snake_to_camel(name): value
            for name, value in zip(cls.names, cls.values)
        }


class BaseNote(models.Model):
    class Types(IntegerEnum):
        PUBLIC = 1, _('Public note')
        PRIVATE = 2, _('Private note')

    text = models.TextField()
    type = models.IntegerField(choices=Types.choices)
    date_created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey('auth.User', null=True, on_delete=models.SET_NULL, related_name='+')

    def __str__(self):
        return f'#{self.id}: {self.text} at {self.date_created.date()}'

    class Meta:
        abstract = True


class RelationshipQuerySet(models.QuerySet):
    def with_people(self):
        return self.select_related('first_person', 'second_person')

    def for_people(self, people, require_visible=True):
        people_pks = people.values_list('pk', flat=True)
        qs = self.filter(
            Q(first_person__in=people_pks) | Q(second_person__in=people_pks)
        )
        if require_visible:
            qs = qs.filter(first_person__visible=True, second_person__visible=True)
        return qs

    def with_status_for_date(self, date=timezone.localdate()):
        return self.prefetch_related(
            Prefetch(
                'statuses',
                queryset=RelationshipStatus.objects.for_date(date).order_by('relationship', '-date_start').distinct('relationship'),
                to_attr='current_status'
            )
        )

    def with_recent_statuses(self):
        return self.prefetch_related(
            Prefetch(
                'statuses',
                queryset=RelationshipStatus.objects.with_duration().order_by('relationship', '-date_start'),
                to_attr='recent_statuses'
            )
        )

    def for_graph_serialization(self, people):
        return self.with_people().for_people(people).with_recent_statuses()


class Relationship(models.Model):
    first_person = models.ForeignKey('people.Person', related_name='relationships_as_first', on_delete=models.CASCADE)
    second_person = models.ForeignKey('people.Person', related_name='relationships_as_second', on_delete=models.CASCADE)

    objects = RelationshipQuerySet.as_manager()

    def __str__(self):
        return f'{self.first_person} <-> {self.second_person}'


class RelationshipStatusNote(BaseNote):

    class Reasons(IntegerEnum):
        STATUS_START = 1, _('Note on relationship start')
        STATUS_END = 2, _('Note on relationship end')
        OTHER = 3, _('Unspecified reason')

    reason = models.IntegerField(choices=Reasons.choices)
    status = models.ForeignKey('people.RelationshipStatus', related_name='notes', on_delete=models.CASCADE)


class RelationshipStatusQuerySet(models.QuerySet):
    def for_date(self, date):
        return self.filter(
            date_start__lte=date
        ).exclude(
            date_end__lt=date
        )

    def with_duration(self):
        return self.annotate(
            duration=Coalesce(F('date_end'), timezone.localdate()) - F('date_start'),
        )


class RelationshipStatus(models.Model):

    class StatusChoices(IntegerEnum):
        BLOOD_RELATIVE = 1, _('Blood relatives')
        SIBLING = 2, _('Siblings')
        PARENT_CHILD = 3, _('Parent-child')
        MARRIED = 4, _('Married')
        ENGAGED = 5, _('Engaged')
        DATING = 6, _('Dating')
        RUMOUR = 7, _('Rumour')

    relationship = models.ForeignKey('people.Relationship', related_name='statuses', on_delete=models.CASCADE)
    status = models.IntegerField(choices=StatusChoices.choices)

    date_start = models.DateField(null=True, blank=True)
    date_end = models.DateField(null=True, blank=True)

    objects = RelationshipStatusQuerySet.as_manager()

    def __str__(self):
        return f'{self.relationship} {self.get_status_display()} from {self.date_start} to {self.date_end}'

    class Meta:
        verbose_name_plural = "relationship statuses"
        get_latest_by = ('date_end', 'date_start')


class PersonNote(BaseNote):
    person = models.ForeignKey('people.Person', related_name='notes', on_delete=models.CASCADE)


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

    def with_visible_memberships(self):
        return self.prefetch_related(
            Prefetch(
                'memberships',
                queryset=GroupMembership.objects.select_related('group').filter(group__visible=True).with_duration(),
                to_attr='visible_memberships'
            )
        )

    def with_age(self):
        return self.annotate(
            age=Coalesce(F('death_date'), timezone.localdate()) - Coalesce(F('birth_date'), timezone.localdate())
        )

    def for_graph_serialization(self):
        return self.filter(visible=True).with_visible_memberships().with_age().order_by('pk')


class Person(models.Model):
    class Genders(IntegerEnum):
        MALE = 1, _('Male')
        FEMALE = 2, _('Female')
        OTHER = 3, _('Other')

    first_name = models.CharField(max_length=128)
    last_name = models.CharField(max_length=128)
    maiden_name = models.CharField(max_length=128, blank=True, null=True)

    nickname = models.CharField(max_length=128, null=True, blank=True)

    gender = models.IntegerField(choices=Genders.choices)

    birth_date = models.DateField(null=True, blank=True)
    death_date = models.DateField(null=True, blank=True)

    visible = models.BooleanField(default=True)

    objects = PersonQuerySet.as_manager()

    def __str__(self):
        return f'{self.nickname or (self.first_name + self.last_name)}'

    class Meta:
        verbose_name_plural = "people"
        unique_together = ('first_name', 'last_name', 'nickname')


class Group(models.Model):

    class Categories(IntegerEnum):
        ELEMENTARY_SCHOOL = 1, _('Elementary school')
        HIGH_SCHOOL = 2, _('High school')
        UNIVERSITY = 3, _('University')
        SEMINAR = 4, _('Seminar')
        OTHER = 5, _('Other')

    category = models.IntegerField(choices=Categories.choices)

    parent = models.ForeignKey('people.Group', null=True, blank=True, related_name='children', on_delete=models.SET_NULL)
    name = models.CharField(max_length=256, unique=True)

    visible = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.name}'


class GroupMembershipNote(BaseNote):
    membership = models.ForeignKey('people.GroupMembership', related_name='notes', on_delete=models.CASCADE)


class GroupMembershipQuerySet(models.QuerySet):
    def with_duration(self):
        return self.annotate(
            duration=Coalesce(F('date_ended'), timezone.localdate()) - Coalesce(F('date_started'), timezone.localdate()),
        )


class GroupMembership(models.Model):
    person = models.ForeignKey('people.Person', related_name='memberships', on_delete=models.CASCADE)
    group = models.ForeignKey('people.Group', related_name='memberships', on_delete=models.CASCADE)

    date_started = models.DateField(null=True, blank=True)
    date_ended = models.DateField(null=True, blank=True)

    objects = GroupMembershipQuerySet.as_manager()

    class Meta:
        unique_together = ('person', 'group')


class VerificationToken(models.Model):
    token = models.CharField(max_length=128, default=random_token)
    valid_until = models.DateTimeField()
