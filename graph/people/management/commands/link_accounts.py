from django.contrib.auth.models import User
from django.core.management import BaseCommand
from django.db import transaction

from people.models import Person


class Command(BaseCommand):
    @transaction.atomic
    def handle(self, *args, **options):
        n = int(input())

        for _ in range(n):
            account_id, person_id = [int(x) for x in input().split()]

            u = User.objects.get(id=account_id)
            p = Person.objects.get(id=person_id)

            print(f'{u.first_name} {u.last_name} -> {p.first_name} {p.last_name}')

            p.account = u
            p.save()
