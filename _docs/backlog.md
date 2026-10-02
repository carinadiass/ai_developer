# Backlog: Household Chores Manager (Django)

A small, ordered backlog for the MVP, based on [plan.md](plan.md). Each task should be small enough for one sitting and end with something that works.

Assumptions (revisit when the open questions in the plan are answered):

- One account per roommate, using Django's built-in `User` and auth.
- Chores start with **manual assignment**, since every other assignment option builds on it. Rotation can be added later (task 9).

## MVP

### 1. Core data models
Create the `Household`, `Chore` and `ChoreAssignment` models in the `chores` app, and register them in the Django admin.
- `Household`: name, members (many-to-many with `User`)
- `Chore`: household, title, description, frequency (once/daily/weekly)
- `ChoreAssignment`: chore, assignee, due date, completed at (nullable)
- **Done when:** migrations run, and you can create a household, chores and assignments in `/admin`.

### 2. User accounts
Add sign up, log in and log out using `django.contrib.auth`, with basic templates.
- **Done when:** a new roommate can register, log in and log out.

### 3. Create and join a household
Let a logged-in user create a household or join one with an invite code.
- **Done when:** two users can end up in the same household.

### 4. Chore list (CRUD)
Pages to list, add, edit and delete the household's chores. Only members of the household can see or change them.
- **Done when:** a member can manage chores and non-members get a 403 or 404.

### 5. Assign chores
Assign a chore to a household member with a due date.
- **Done when:** an assignment appears on the household dashboard.

### 6. Mark chores done
A "Done" button that sets `completed_at`. Overdue assignments are highlighted.
- **Done when:** completed and overdue states show correctly.

### 7. Dashboard
A household home page with "My chores", "Everyone's chores this week" and "Overdue".
- **Done when:** each roommate sees their tasks at a glance after logging in.

### 8. Tests
Model and view tests for permissions, assignment and completion.
- **Done when:** `python manage.py test` passes.

## Later

9. Automatic rotation of recurring chores
10. Points per chore and workload balance
11. Email reminders for upcoming and overdue chores
12. Deploy (e.g. Render or PythonAnywhere)
