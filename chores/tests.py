from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Chore, ChoreAssignment, Household

User = get_user_model()


class ChoresTestCase(TestCase):
    def setUp(self):
        self.alice = User.objects.create_user("alice", password="pw")
        self.bob = User.objects.create_user("bob", password="pw")
        self.household = Household.objects.create(name="Flat 3B")
        self.household.members.add(self.alice, self.bob)
        self.chore = Chore.objects.create(
            household=self.household, title="Take out trash", frequency="weekly"
        )


class StrTests(ChoresTestCase):
    def test_household_str(self):
        self.assertEqual(str(self.household), "Flat 3B")

    def test_chore_str(self):
        self.assertEqual(str(self.chore), "Take out trash")

    def test_assignment_str(self):
        assignment = ChoreAssignment.objects.create(
            chore=self.chore, assignee=self.alice, due_date=date(2026, 10, 5)
        )
        self.assertEqual(
            str(assignment), "Take out trash → alice (due 2026-10-05)"
        )


class ChoreFieldTests(ChoresTestCase):
    def test_default_frequency_is_once(self):
        chore = Chore.objects.create(household=self.household, title="Dishes")
        self.assertEqual(chore.frequency, Chore.Frequency.ONCE)

    def test_blank_description_is_valid(self):
        chore = Chore(household=self.household, title="Dishes")
        chore.full_clean()  # does not raise

    def test_invalid_frequency_fails_validation(self):
        chore = Chore(household=self.household, title="Dishes", frequency="hourly")
        with self.assertRaises(ValidationError):
            chore.full_clean()


class MembershipTests(ChoresTestCase):
    def test_household_lists_members(self):
        self.assertQuerySetEqual(
            self.household.members.order_by("username"),
            [self.alice, self.bob],
        )

    def test_user_can_belong_to_several_households(self):
        other = Household.objects.create(name="Beach house")
        other.members.add(self.alice)
        self.assertEqual(self.alice.households.count(), 2)
        self.assertEqual(self.bob.households.count(), 1)


class CascadeDeleteTests(ChoresTestCase):
    def setUp(self):
        super().setUp()
        self.assignment = ChoreAssignment.objects.create(
            chore=self.chore, assignee=self.alice, due_date=date.today()
        )

    def test_deleting_household_removes_chores_and_assignments(self):
        self.household.delete()
        self.assertFalse(Chore.objects.exists())
        self.assertFalse(ChoreAssignment.objects.exists())

    def test_deleting_chore_removes_assignments(self):
        self.chore.delete()
        self.assertFalse(ChoreAssignment.objects.exists())

    def test_deleting_user_removes_their_assignments_only(self):
        ChoreAssignment.objects.create(
            chore=self.chore, assignee=self.bob, due_date=date.today()
        )
        self.alice.delete()
        self.assertEqual(
            list(ChoreAssignment.objects.values_list("assignee__username", flat=True)),
            ["bob"],
        )
        self.assertTrue(Chore.objects.filter(pk=self.chore.pk).exists())


class OrderingTests(ChoresTestCase):
    def test_chores_ordered_by_title(self):
        Chore.objects.create(household=self.household, title="Vacuum")
        Chore.objects.create(household=self.household, title="Dishes")
        titles = list(Chore.objects.values_list("title", flat=True))
        self.assertEqual(titles, ["Dishes", "Take out trash", "Vacuum"])

    def test_assignments_ordered_by_due_date(self):
        today = date.today()
        later = ChoreAssignment.objects.create(
            chore=self.chore, assignee=self.alice, due_date=today + timedelta(days=3)
        )
        sooner = ChoreAssignment.objects.create(
            chore=self.chore, assignee=self.bob, due_date=today
        )
        self.assertEqual(list(ChoreAssignment.objects.all()), [sooner, later])


class CompletionTests(ChoresTestCase):
    def test_new_assignment_is_not_completed(self):
        assignment = ChoreAssignment.objects.create(
            chore=self.chore, assignee=self.alice, due_date=date.today()
        )
        self.assertFalse(assignment.is_completed)

    def test_assignment_with_completed_at_is_completed(self):
        assignment = ChoreAssignment.objects.create(
            chore=self.chore,
            assignee=self.alice,
            due_date=date.today(),
            completed_at=timezone.now(),
        )
        self.assertTrue(assignment.is_completed)


class AdminTests(ChoresTestCase):
    MODELS = ["household", "chore", "choreassignment"]

    def setUp(self):
        super().setUp()
        self.admin = User.objects.create_superuser("admin", password="pw")

    def test_superuser_can_open_changelist_and_add_pages(self):
        self.client.force_login(self.admin)
        for model in self.MODELS:
            for view in ["changelist", "add"]:
                with self.subTest(model=model, view=view):
                    url = reverse(f"admin:chores_{model}_{view}")
                    self.assertEqual(self.client.get(url).status_code, 200)

    def test_non_staff_user_is_redirected_to_login(self):
        self.client.force_login(self.alice)
        url = reverse("admin:chores_chore_changelist")
        response = self.client.get(url)
        self.assertRedirects(response, f"{reverse('admin:login')}?next={url}")

    def test_chore_search(self):
        Chore.objects.create(household=self.household, title="Vacuum")
        self.client.force_login(self.admin)
        response = self.client.get(
            reverse("admin:chores_chore_changelist"), {"q": "trash"}
        )
        self.assertContains(response, "Take out trash")
        self.assertNotContains(response, "Vacuum")

    def test_chore_filter_by_frequency(self):
        Chore.objects.create(household=self.household, title="Vacuum", frequency="daily")
        self.client.force_login(self.admin)
        response = self.client.get(
            reverse("admin:chores_chore_changelist"), {"frequency__exact": "daily"}
        )
        self.assertContains(response, "Vacuum")
        self.assertNotContains(response, "Take out trash")
