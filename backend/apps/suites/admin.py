from django.contrib import admin

from .models import CalendarEvent, Schedule, Suite, SuiteNotification, SuiteTestCase


class SuiteTestCaseInline(admin.TabularInline):
    model = SuiteTestCase
    extra = 0


@admin.register(Suite)
class SuiteAdmin(admin.ModelAdmin):
    list_display = ("name", "project", "parallelism", "retries")
    search_fields = ("name", "project__name")
    list_filter = ("project",)
    prepopulated_fields = {"slug": ("name",)}
    inlines = [SuiteTestCaseInline]


admin.site.register(Schedule)
admin.site.register(SuiteNotification)
admin.site.register(CalendarEvent)
