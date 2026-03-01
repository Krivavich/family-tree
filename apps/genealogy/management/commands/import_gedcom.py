from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from apps.genealogy.models import Tree
from apps.genealogy.services.gedcom import import_stub_gedcom_lines


class Command(BaseCommand):
    help = "Import people from GEDCOM file (basic MVP parser)"

    def add_arguments(self, parser):
        parser.add_argument("tree_id", type=int)
        parser.add_argument("input", type=str)

    def handle(self, *args, **options):
        tree = Tree.objects.filter(id=options["tree_id"]).first()
        if not tree:
            raise CommandError("Tree not found")

        path = Path(options["input"])
        if not path.exists():
            raise CommandError("Input GEDCOM not found")

        created = import_stub_gedcom_lines(tree, path.read_text(encoding="utf-8").splitlines())
        self.stdout.write(self.style.SUCCESS(f"Imported/parsed {created} records"))
