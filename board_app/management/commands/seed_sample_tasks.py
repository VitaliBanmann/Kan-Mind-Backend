from datetime import date, timedelta

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from auth_app.models import User
from board_app.models import Board
from task_app.models import Task


class Command(BaseCommand):
    help = (
        'Create five sample tasks for an existing user without duplicating them.'
    )

    def add_arguments(self, parser):
        parser.add_argument('--email', required=True)
        parser.add_argument('--board-title', default='KanMind Sample Board')

    @transaction.atomic
    def handle(self, *args, **options):
        email = options['email']
        board_title = options['board_title']

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist as exc:
            raise CommandError(
                f'No user found for {email}. Register this user first.'
            ) from exc

        board, created = Board.objects.get_or_create(
            title=board_title,
            owner=user,
        )
        board.members.add(user)

        samples = [
            (
                'Einkaufen gehen',
                'Obst, Gemuese, Brot, Milch und Zutaten fuer das Abendessen einkaufen.',
                'high',
                'to-do',
            ),
            (
                'Hausputz erledigen',
                'Wohnzimmer und Bad reinigen, Staub wischen und den Boden saugen.',
                'medium',
                'in-progress',
            ),
            (
                'Waesche waschen',
                'Eine Maschine waeschen, aufhaengen und anschliessend zusammenlegen.',
                'low',
                'to-do',
            ),
            (
                'Arzttermin vereinbaren',
                'In der Praxis anrufen und einen passenden Termin fuer die '
                'Kontrolluntersuchung vereinbaren.',
                'high',
                'review',
            ),
            (
                'Abendessen vorbereiten',
                'Rezept aussuchen, Zutaten bereitstellen und das Abendessen '
                'fuer heute kochen.',
                'medium',
                'done',
            ),
        ]

        created_tasks = 0
        for title, description, priority, status in samples:
            _, was_created = Task.objects.get_or_create(
                board=board,
                creator=user,
                title=title,
                defaults={
                    'description': description,
                    'priority': priority,
                    'status': status,
                    'assignee': user,
                    'reviewer': user,
                    'due_date': date.today() + timedelta(days=7),
                },
            )
            created_tasks += int(was_created)

        board_state = 'created' if created else 'already existed'
        self.stdout.write(
            self.style.SUCCESS(
                f'Board {board_state}; created {created_tasks} new sample tasks.'
            )
        )
