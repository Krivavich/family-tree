from dataclasses import dataclass
from datetime import date
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

    family_idx = 1
    for rel in tree.relationships.filter(relation_type=Relationship.Type.PARENT).select_related("from_person", "to_person"):
        fam = f"@F{family_idx}@"
        family_idx += 1
        lines.append(f"0 {fam} FAM")
        lines.append(f"1 HUSB {id_map.get(rel.from_person_id, '@I0@')}")
        lines.append(f"1 CHIL {id_map.get(rel.to_person_id, '@I0@')}")

    lines.append("0 TRLR")
    return GedcomExportResult(content="\n".join(lines) + "\n", people_count=len(people))


def _parse_iso_date(raw: str):
    try:
        return date.fromisoformat(raw)
    except Exception:
        return None


def import_stub_gedcom_lines(tree: Tree, lines: Iterable[str]) -> int:
    person_map: dict[str, Person] = {}
    family_parents: dict[str, Person] = {}
    family_children: list[tuple[str, Person]] = []

    current_entity = None
    current_id = None
    pending_name = None
    pending_birth = None
    pending_death = None
    imported_people = 0

    def flush_person():
        nonlocal pending_name, pending_birth, pending_death, current_id, imported_people
        if current_entity == "INDI" and current_id and pending_name:
            first = pending_name.split("/")[0].strip() or "Unknown"
            last = pending_name.split("/")[1].strip() if "/" in pending_name else ""
            person, _ = Person.objects.get_or_create(
                tree=tree,
                first_name=first,
                last_name=last,
                defaults={"birth_date": pending_birth, "death_date": pending_death},
            )
            person_map[current_id] = person
            imported_people += 1

    prev_tag = None
    for line in lines:
        line = line.strip()
        if not line:
            continue
        parts = line.split(" ", 2)
        level = parts[0]

        if level == "0":
            flush_person()
            pending_name = None
            pending_birth = None
            pending_death = None
            prev_tag = None
            current_id = parts[1] if len(parts) > 2 else None
            current_entity = parts[2] if len(parts) > 2 else parts[1]
            continue

        if current_entity == "INDI":
            if parts[1] == "NAME" and len(parts) > 2:
                pending_name = parts[2]
            elif parts[1] in ("BIRT", "DEAT"):
                prev_tag = parts[1]
            elif parts[1] == "DATE" and len(parts) > 2:
                parsed = _parse_iso_date(parts[2])
                if prev_tag == "BIRT":
                    pending_birth = parsed
                elif prev_tag == "DEAT":
                    pending_death = parsed

        if current_entity == "FAM" and current_id:
            if parts[1] == "HUSB" and len(parts) > 2:
                parent = person_map.get(parts[2])
                if parent:
                    family_parents[current_id] = parent
            elif parts[1] == "CHIL" and len(parts) > 2:
                child = person_map.get(parts[2])
                if child:
                    family_children.append((current_id, child))

    flush_person()

    for fam_id, child in family_children:
        parent = family_parents.get(fam_id)
        if parent and parent.tree_id == child.tree_id:
            Relationship.objects.get_or_create(
                tree=tree,
                from_person=parent,
                to_person=child,
                relation_type=Relationship.Type.PARENT,
            )

    return imported_people
