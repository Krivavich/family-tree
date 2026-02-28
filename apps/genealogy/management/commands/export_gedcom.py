from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from apps.genealogy.models import Tree
from apps.genealogy.services.gedcom import export_tree_to_gedcom


class Command(BaseCommand):
    help = "Export tree to GEDCOM file"

    def add_arguments(self, parser):
        parser.add_argument("tree_id", type=int)
        parser.add_argument("--output", type=str, default="tree_export.ged")

    def handle(self, *args, **options):
        tree = Tree.objects.filter(id=options["tree_id"]).first()
        if not tree:
            raise CommandError("Tree not found")

        result = export_tree_to_gedcom(tree)
        output = Path(options["output"])
        output.write_text(result.content, encoding="utf-8")
        self.stdout.write(self.style.SUCCESS(f"Exported {result.people_count} people to {output}"))
