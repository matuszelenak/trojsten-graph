import csv

from django.core.management import BaseCommand
from django.db.models import Value, CharField
from django.db.models.functions import Concat

from people.models import Person


class Command(BaseCommand):
    def handle(self, *args, **options):
        qs = Person.objects\
            .select_related('account')\
            .annotate(full_name=Concat('first_name', Value(' '), 'last_name'))\
            .order_by('last_name', 'first_name')\
            .values('nickname')

        with open('nicknames.csv', 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=['nickname'])

            writer.writeheader()
            for row in qs:
                writer.writerow(row)
