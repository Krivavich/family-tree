from datetime import date

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import RequestFactory, TestCase

from .api import EventSerializer
from .forms import EventForm, PersonForm, RelationshipForm
from .models import Event, MediaAsset, Person, ProposedChange, Tree, TreeMembership
from .services.insights import calculate_person_completeness
from .services.proposed_changes import apply_proposed_change


class PermissionAndMergeFlowTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.owner = User.objects.create_user(username="owner", password="pass-12345")
        self.editor = User.objects.create_user(username="editor", password="pass-12345")
        self.viewer = User.objects.create_user(username="viewer", password="pass-12345")
        self.tree = Tree.objects.create(name="Tree", owner=self.owner)
        TreeMembership.objects.create(tree=self.tree, user=self.owner, role=TreeMembership.Role.OWNER)
        TreeMembership.objects.create(tree=self.tree, user=self.editor, role=TreeMembership.Role.EDITOR)
        TreeMembership.objects.create(tree=self.tree, user=self.viewer, role=TreeMembership.Role.VIEWER)
        self.person = Person.objects.create(tree=self.tree, first_name="Ivan", last_name="Petrov")

    def test_apply_proposed_change_updates_person(self):
        change = ProposedChange.objects.create(
            tree=self.tree,
            proposer=self.editor,
            target_model="person",
            target_id=self.person.id,
            change_payload={"first_name": "Иван", "biography": "Updated"},
        )
        apply_proposed_change(change, reviewer=self.owner)
        self.person.refresh_from_db()
        change.refresh_from_db()
        self.assertEqual(self.person.first_name, "Иван")
        self.assertEqual(change.status, ProposedChange.Status.APPROVED)


class MediaValidationTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.owner = User.objects.create_user(username="owner2", password="pass-12345")
        self.tree = Tree.objects.create(name="Tree2", owner=self.owner)
        TreeMembership.objects.create(tree=self.tree, user=self.owner, role=TreeMembership.Role.OWNER)
        self.person = Person.objects.create(tree=self.tree, first_name="Anna", last_name="S")

    def test_eicar_signature_blocked(self):
        payload = b"X5O!P%@AP[4\\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*"
        upload = SimpleUploadedFile("test.txt", payload)
        media = MediaAsset(person=self.person, title="bad", file=upload, uploaded_by=self.owner)
        with self.assertRaises(ValidationError):
            media.full_clean()


class EventAndInsightsTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.owner = User.objects.create_user(username="owner3", password="pass-12345")
        self.tree = Tree.objects.create(name="Tree3", owner=self.owner)
        TreeMembership.objects.create(tree=self.tree, user=self.owner, role=TreeMembership.Role.OWNER)
        self.person = Person.objects.create(tree=self.tree, first_name="Olga", last_name="K")

    def test_event_creation(self):
        event = Event.objects.create(
            person=self.person,
            event_type=Event.Type.BIRTH,
            event_date=date(1990, 1, 1),
            place="Moscow",
        )
        self.assertEqual(event.person_id, self.person.id)

    def test_completeness_score(self):
        c = calculate_person_completeness(self.person)
        self.assertLess(c.score, 100)


class RoleWriteRestrictionTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.owner = User.objects.create_user(username="owner4", password="pass-12345")
        self.viewer = User.objects.create_user(username="viewer4", password="pass-12345")
        self.tree = Tree.objects.create(name="Tree4", owner=self.owner)
        TreeMembership.objects.create(tree=self.tree, user=self.owner, role=TreeMembership.Role.OWNER)
        TreeMembership.objects.create(tree=self.tree, user=self.viewer, role=TreeMembership.Role.VIEWER)
        self.person = Person.objects.create(tree=self.tree, first_name="Petr", last_name="V")

    def test_viewer_cannot_use_write_forms(self):
        person_form = PersonForm(user=self.viewer)
        relationship_form = RelationshipForm(user=self.viewer)
        event_form = EventForm(user=self.viewer)
        self.assertEqual(person_form.fields["tree"].queryset.count(), 0)
        self.assertEqual(relationship_form.fields["tree"].queryset.count(), 0)
        self.assertEqual(event_form.fields["person"].queryset.count(), 0)

    def test_event_serializer_blocks_viewer_write(self):
        request = RequestFactory().post("/api/events/")
        request.user = self.viewer
        serializer = EventSerializer(
            data={"person": self.person.id, "event_type": Event.Type.BIRTH},
            context={"request": request},
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("person", serializer.errors)
