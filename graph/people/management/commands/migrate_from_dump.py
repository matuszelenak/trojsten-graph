import itertools
import json
from collections import defaultdict
from datetime import datetime

from django.core.management import BaseCommand
from django.db import transaction

from people.models import Person, Group, GroupMembership, Relationship, RelationshipStatus, PersonNote, GroupMembershipNote, RelationshipStatusNote


def str_to_date(s):
    if s:
        return datetime.strptime(s, '%Y-%m-%d').date()


def sex_to_gender(sex):
    if sex == 'M':
        return Person.Genders.MALE
    if sex == 'F':
        return Person.Genders.FEMALE
    return Person.Genders.OTHER


def event_type_to_new_status(event_type):
    return {
        'SIB': RelationshipStatus.StatusChoices.SIBLING,
        'DAT': RelationshipStatus.StatusChoices.DATING,
        'DRB': RelationshipStatus.StatusChoices.RUMOUR,
        'NDR': None,
        'BRE': None,
        'ENG': RelationshipStatus.StatusChoices.ENGAGED,
        'MAR': RelationshipStatus.StatusChoices.MARRIED,
        'DIV': None,
        'CHI': RelationshipStatus.StatusChoices.PARENT_CHILD,
        'REL': RelationshipStatus.StatusChoices.BLOOD_RELATIVE,
    }[event_type]


def category_to_enum(cat):
    return {
        'U': Group.Categories.UNIVERSITY,
        'E': Group.Categories.ELEMENTARY_SCHOOL,
        'H': Group.Categories.HIGH_SCHOOL,
        'S': Group.Categories.SEMINAR,
        'O': Group.Categories.OTHER
    }[cat]


def get_by_old_pk(instances, pk):
    return next(filter(lambda x: x.old_pk == pk, instances), None)


def import_people(people):
    Person.qs.all().delete()
    PersonNote.objects.all().delete()
    imported_people = []
    imported_notes = []
    for person in people:
        f = person['fields']
        p = Person.qs.create(
            first_name=f['name'],
            last_name=f['surname'],
            maiden_name=f['maidenName'],
            nickname=f['nickname'] if f['nickname'] != f['name'] + ' ' + f['surname'] else None,
            gender=sex_to_gender(f['sex']),
            birth_date=str_to_date(f['birthDate']),
            death_date=str_to_date(f['deathDate']),
            visible=f['visible']
        )
        setattr(p, 'old_pk', person['pk'])
        imported_people.append(p)

        if f['comment']:
            imported_notes.append(
                PersonNote(
                    type=PersonNote.Types.PUBLIC,
                    person=p,
                    text=f['comment']
                )
            )
        if f['dataComment']:
            imported_notes.append(
                PersonNote(
                    type=PersonNote.Types.PRIVATE,
                    person=p,
                    text=f['dataComment'],
                )
            )
    PersonNote.objects.bulk_create(imported_notes)

    return imported_people


def import_groups(groups):
    Group.objects.all().delete()
    imported_groups = []
    parent_links = []
    for group in groups:
        f = group['fields']
        g = Group.objects.create(
            name=f['name'],
            category=category_to_enum(f['category']),
            visible=f['visible'],
        )
        setattr(g, 'old_pk', group['pk'])
        imported_groups.append(g)

        if f['parent']:
            parent_links.append((f['parent'], group['pk']))

    for group_a, group_b in itertools.product(imported_groups, repeat=2):
        if (group_a.old_pk, group_b.old_pk) in parent_links:
            print(f'{group_a} parent of  {group_b}')
            group_b.parent = group_a
            group_b.save()

    return imported_groups


def import_memberships(memberships, new_people, new_groups):
    GroupMembership.objects.all().delete()
    GroupMembershipNote.objects.all().delete()

    imported_notes = []
    for membership in memberships:
        f = membership['fields']
        person = get_by_old_pk(new_people, f['person'])
        group = get_by_old_pk(new_groups, f['group'])
        m = GroupMembership.objects.create(
            person=person,
            group=group,
            date_started=str_to_date(f['startDate']),
            date_ended=str_to_date(f['endDate'])
        )

        if f['comment']:
            imported_notes.append(
                GroupMembershipNote(
                    type=GroupMembershipNote.Types.PUBLIC,
                    membership=m,
                    text=f['comment']
                )
            )
        if f['dataComment']:
            imported_notes.append(
                GroupMembershipNote(
                    type=GroupMembershipNote.Types.PRIVATE,
                    membership=m,
                    text=f['dataComment'],
                )
            )
    GroupMembershipNote.objects.bulk_create(imported_notes)


def import_relationships(events, people):
    Relationship.objects.all().delete()
    RelationshipStatus.objects.all().delete()
    RelationshipStatusNote.objects.all().delete()

    events_per_pair = defaultdict(list)
    for event in events:
        f = event['fields']
        key = ';'.join(map(str, sorted([f['personFrom'], f['personTo']])))
        events_per_pair[key].append({
            'date': str_to_date(f['date']),
            'comment': f['comment'],
            'data_comment': f['dataComment'],
            'visible': f['visible'],
            'type': f['type']
        })

    for pair, events in events_per_pair.items():
        first_pk, second_pk = tuple(map(int, pair.split(';')))
        first, second = get_by_old_pk(people, first_pk), get_by_old_pk(people, second_pk)
        sorted_events = sorted(events, key=lambda x: x['date'])

        cutoff = 0
        for i, event in enumerate(sorted_events):
            if not event_type_to_new_status(event['type']):
                print(f'Skipping event {event} for {first} {second}')
                cutoff += 1
            else:
                break

        sorted_events = sorted_events[cutoff::]

        if not sorted_events:
            continue

        rel = Relationship.objects.create(
            first_person=first,
            second_person=second
        )

        print(rel, [x['type'] for x in sorted_events])
        first_event = sorted_events[0]

        previous_status = RelationshipStatus.objects.create(
            relationship=rel,
            date_start=first_event['date'],
            status=event_type_to_new_status(first_event['type']),
            visible=first_event['visible']
        )
        if first_event['comment']:
            RelationshipStatusNote.objects.create(
                status=previous_status,
                text=first_event['comment'],
                type=RelationshipStatusNote.Types.PUBLIC,
                reason=RelationshipStatusNote.Reasons.STATUS_START
            )
        if first_event['data_comment']:
            RelationshipStatusNote.objects.create(
                status=previous_status,
                text=first_event['data_comment'],
                type=RelationshipStatusNote.Types.PRIVATE,
                reason=RelationshipStatusNote.Reasons.STATUS_START
            )

        for next_event in sorted_events[1:]:
            new_status_type = event_type_to_new_status(next_event['type'])

            if new_status_type:
                new_status = RelationshipStatus.objects.create(
                    relationship=rel,
                    date_start=next_event['date'],
                    status=new_status_type,
                    visible=next_event['visible']
                )
                note_kwargs = dict(
                    reason=RelationshipStatusNote.Reasons.STATUS_START,
                    status=new_status
                )
            else:
                assert previous_status.status in (RelationshipStatus.StatusChoices.DATING, RelationshipStatus.StatusChoices.RUMOUR, RelationshipStatus.StatusChoices.ENGAGED, RelationshipStatus.StatusChoices.MARRIED)
                new_status = None
                note_kwargs = dict(
                    reason=RelationshipStatusNote.Reasons.STATUS_END,
                    status=previous_status
                )
            if previous_status:
                previous_status.date_end = next_event['date']
                previous_status.visible &= next_event['visible']
                previous_status.save()

            if next_event['comment']:
                RelationshipStatusNote.objects.create(
                    text=next_event['comment'],
                    type=RelationshipStatusNote.Types.PUBLIC,
                    **note_kwargs
                )
            if next_event['data_comment']:
                RelationshipStatusNote.objects.create(
                    text=next_event['data_comment'],
                    type=RelationshipStatusNote.Types.PRIVATE,
                    **note_kwargs
                )

            previous_status = new_status


class Command(BaseCommand):
    @transaction.atomic
    def handle(self, *args, **kwargs):
        j = json.load(open('data_16_01_2020_rano.data'))

        people = import_people([x for x in j if x['model'] == 'graph.person'])
        groups = import_groups([x for x in j if x['model'] == 'graph.group'])
        import_memberships([x for x in j if x['model'] == 'graph.membership'], people, groups)
        import_relationships([x for x in j if x['model'] == 'graph.event'], people)
