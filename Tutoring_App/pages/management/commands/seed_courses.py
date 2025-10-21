from django.core.management.base import BaseCommand

from pages.models import Course

COURSES = [
    ("CSCI 101", "Introduction to Computer Science"),
    ("CSCI 258", "Web Development"),
    ("CSCI 232", "Data Structures"),
    ("LANG 201", "English for Extraterrestrials"),
    ("GEO 221", "Geography of Erebus"),
    ("PETS 456", "How to feed your pets"),
]


class Command(BaseCommand):
    help = "Seed default Course rows for TA signup"

    def handle(self, *args, **options):
        created = 0
        updated = 0
        for code, name in COURSES:
            obj, was_created = Course.objects.update_or_create(
                code=code, defaults={"name": name}
            )
            if was_created:
                created += 1
            else:
                updated += 1
        self.stdout.write(
            self.style.SUCCESS(
                f"Courses seeded successfully. Created: {created}, Updated: {updated}."
            )
        )
