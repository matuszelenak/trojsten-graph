from django.core.management import BaseCommand
from django.db import transaction

from people.models import RelationshipStatus, ManagementAuthority


class Command(BaseCommand):
    @transaction.atomic
    def handle(self, *args, **options):
        authorities = []

        for rel in RelationshipStatus.objects.select_related('relationship__first_person','relationship__second_person').filter(status=RelationshipStatus.StatusChoices.PARENT_CHILD):
            first, second = rel.relationship.first_person, rel.relationship.second_person

            if not first.birth_date or not second.birth_date:
                # Cant determine who is parent and who child
                continue

            if str(first.birth_date) < str(second.birth_date):
                m = ManagementAuthority(
                    manager=first,
                    subject=second
                )
            else:
                m = ManagementAuthority(
                    manager=second,
                    subject=first
                )

            authorities.append(m)

        ManagementAuthority.objects.bulk_create(authorities, batch_size=500)
