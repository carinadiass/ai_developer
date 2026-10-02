from django.contrib import admin

from .models import Chore, ChoreAssignment, Household


@admin.register(Household)
class HouseholdAdmin(admin.ModelAdmin):
    list_display = ["name", "created_at"]
    filter_horizontal = ["members"]


@admin.register(Chore)
class ChoreAdmin(admin.ModelAdmin):
    list_display = ["title", "household", "frequency"]
    list_filter = ["household", "frequency"]
    search_fields = ["title"]


@admin.register(ChoreAssignment)
class ChoreAssignmentAdmin(admin.ModelAdmin):
    list_display = ["chore", "assignee", "due_date", "completed_at"]
    list_filter = ["chore__household", "assignee"]
    date_hierarchy = "due_date"
