from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ValidationError
from django.test import TestCase

from .models import MediaAsset, Person, ProposedChange, Relationship, Tree, TreeMembership
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
