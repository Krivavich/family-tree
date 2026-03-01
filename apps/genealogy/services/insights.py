from dataclasses import dataclass


@dataclass
class PersonCompleteness:
    score: int
    missing: list[str]


def calculate_person_completeness(person) -> PersonCompleteness:
    missing = []
    if not person.birth_date:
        missing.append("дата рождения")
    if not person.biography:
        missing.append("биография")
    if not person.last_name:
        missing.append("фамилия")

    total = 3
    done = total - len(missing)
    return PersonCompleteness(score=int(done / total * 100), missing=missing)
