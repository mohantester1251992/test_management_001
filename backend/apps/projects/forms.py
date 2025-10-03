from __future__ import annotations

from django import forms
from django.utils.text import slugify

from backend.apps.organizations.models import Organization

from .models import Environment, Project


class ProjectForm(forms.ModelForm):
    organization = forms.ModelChoiceField(queryset=Organization.objects.none())

    class Meta:
        model = Project
        fields = ["organization", "name", "slug", "description", "default_base_url", "tags"]

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
        if user.is_superuser:
            qs = Organization.objects.all()
        else:
            qs = Organization.objects.filter(memberships__user=user)
        self.fields["organization"].queryset = qs
        self.fields["slug"].required = False
        for field in self.fields.values():
            field.widget.attrs.setdefault(
                "class",
                "w-full rounded-lg border border-slate-200 dark:border-slate-700 bg-white/80 dark:bg-slate-900/60 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500",
            )

    def save(self, commit: bool = True):
        project = super().save(commit=False)
        if not project.slug:
            project.slug = slugify(project.name)
        project.created_by = self.user
        if commit:
            project.save()
            self.save_m2m()
        return project


class EnvironmentForm(forms.ModelForm):
    class Meta:
        model = Environment
        fields = ["name", "slug", "base_url", "variables", "is_active", "concurrency", "timezone"]

    def __init__(self, project: Project, *args, **kwargs):
        self.project = project
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault(
                "class",
                "w-full rounded-lg border border-slate-200 dark:border-slate-700 bg-white/80 dark:bg-slate-900/60 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500",
            )
        self.fields["slug"].required = False

    def save(self, commit: bool = True):
        environment = super().save(commit=False)
        environment.project = self.project
        if not environment.slug:
            environment.slug = slugify(environment.name)
        if commit:
            environment.save()
            self.save_m2m()
        return environment
