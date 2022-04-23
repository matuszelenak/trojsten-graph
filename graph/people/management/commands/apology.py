from django.conf import settings
from django.core.mail import send_mail
from django.core.management import BaseCommand
from django.db import transaction
from django.db.models import Exists, OuterRef, Q
from django.template.loader import get_template
from django.utils.html import strip_tags

from people.models import Person, ManagementAuthority, GroupMembership, Relationship, RelationshipStatus, ContactEmail
from users.models import Token


class Command(BaseCommand):
    @transaction.atomic
    def handle(self, *args, **options):
        for person in Person.objects.filter(apology_status=Person.ApologyStatus.UNSENT, last_name='Zeleňák'):
            if person.email is not None:
                contact_emails = [person.email]
            else:
                all_contacts = list(ContactEmail.objects.filter(person=person).order_by('-sure_its_active'))
                if len(all_contacts) == 0:
                    break

                if all_contacts[0].sure_its_active:
                    contact_emails = [all_contacts[0].email]
                else:
                    contact_emails = [x.email for x in all_contacts]

            auth_token = Token.create_for_user(
                person,
                token_type=Token.Types.AUTH,
            )
            auth_token.save()

            group_memberships = GroupMembership.objects.select_related('group').filter(
                person=person
            )

            relationships = Relationship.objects.filter(
                Q(first_person=person) | Q(second_person=person)
            )

            managed_people = Person.qs.filter(
                Exists(
                    ManagementAuthority.objects.filter(manager=person, subject=OuterRef('pk'))
                )
            )

            html_message = get_template('people/email/notice_and_apology.html').render(
                {
                    'token': auth_token.token,
                    'person': person,
                    'group_memberships': list(group_memberships),
                    'relationships': [
                        (
                            r.first_person.name if r.second_person == person else r.second_person.name,
                            RelationshipStatus.objects.filter(relationship=r).order_by('date_start')
                        )
                        for r in relationships
                    ],
                    'managed_people': managed_people
                }
            )
            plain_message = strip_tags(html_message)

            print(settings.EMAIL_HOST_USER)
            print(settings.EMAIL_HOST_PASSWORD)

            # raise ValueError

            send_mail(
                'Trojsten Graf - informovanie o použití osobných dát',
                plain_message,
                None,
                contact_emails,
                html_message=html_message
            )

            person.apology_status = Person.ApologyStatus.SENT
            person.save()
