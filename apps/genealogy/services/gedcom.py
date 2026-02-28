from dataclasses import dataclass
from typing import Iterable

from apps.genealogy.models import Person, Relationship, Tree


@dataclass
class GedcomExportResult:
    content: str
    people_count: int


def export_tree_to_gedcom(tree: Tree) -> GedcomExportResult:
    lines = ["0 HEAD", "1 SOUR FAMILY-TREE", "1 GEDC", "2 VERS 5.5.1"]
    people = list(tree.persons.all().order_by("id"))
    id_map = {p.id: f"@I{idx}@" for idx, p in enumerate(people, start=1)}

    for p in people:
        lines.append(f"0 {id_map[p.id]} INDI")
        full_name = f"{p.first_name} /{p.last_name or ''}/".strip()
        lines.append(f"1 NAME {full_name}")
        if p.birth_date:
            lines.extend(["1 BIRT", f"2 DATE {p.birth_date.isoformat()}"])
        if p.death_date:
            lines.extend(["1 DEAT", f"2 DATE {p.death_date.isoformat()}"])

    for idx, rel in enumerate(tree.relationships.filter(relation_type=Relationship.Type.PARENT), start=1):
        fam = f"@F{idx}@"
        lines.append(f"0 {fam} FAM")
        lines.append(f"1 HUSB {id_map.get(rel.from_person_id, '@I0@')}")
        lines.append(f"1 CHIL {id_map.get(rel.to_person_id, '@I0@')}")

    lines.append("0 TRLR")
    return GedcomExportResult(content="\n".join(lines) + "\n", people_count=len(people))


def import_stub_gedcom_lines(tree: Tree, lines: Iterable[str]) -> int:
    created = 0
    for line in lines:
        if " NAME " in line and "/" in line:
            name_part = line.split(" NAME ", 1)[1]
            first = name_part.split("/")[0].strip() or "Unknown"
            last = name_part.split("/")[1].strip() if "/" in name_part else ""
            Person.objects.get_or_create(tree=tree, first_name=first, last_name=last)
            created += 1
    return created
