from django.contrib import admin

from .models import Environment, Locator, Project, Secret


class EnvironmentInline(admin.StackedInline):
    model = Environment
    extra = 0


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("name", "organization", "default_base_url", "created_at")
    list_filter = ("organization",)
    search_fields = ("name", "organization__name")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [EnvironmentInline]


@admin.register(Environment)
class EnvironmentAdmin(admin.ModelAdmin):
    list_display = ("name", "project", "base_url", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "project__name")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Secret)
class SecretAdmin(admin.ModelAdmin):
    list_display = ("name", "project", "key_type", "created_at")
    search_fields = ("name", "project__name")


@admin.register(Locator)
class LocatorAdmin(admin.ModelAdmin):
    list_display = ("name", "project", "strategy", "health_status", "last_checked_at")
    search_fields = ("name", "project__name", "value")
    list_filter = ("strategy", "health_status")
