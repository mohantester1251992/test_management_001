from django.contrib import admin

from .models import AssertionResult, Comment, Dataset, ReusableStep, TestCase, TestStep


class TestStepInline(admin.TabularInline):
    model = TestStep
    extra = 0


@admin.register(TestCase)
class TestCaseAdmin(admin.ModelAdmin):
    list_display = ("name", "project", "created_at", "is_active")
    search_fields = ("name", "project__name")
    list_filter = ("project", "is_active")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [TestStepInline]


@admin.register(Dataset)
class DatasetAdmin(admin.ModelAdmin):
    list_display = ("name", "project", "created_at")
    search_fields = ("name", "project__name")
    prepopulated_fields = {"slug": ("name",)}


admin.site.register(TestStep)
admin.site.register(ReusableStep)
admin.site.register(AssertionResult)
admin.site.register(Comment)
