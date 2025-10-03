from __future__ import annotations

from django import forms

from backend.apps.projects.models import Environment
from backend.apps.testcases.models import TestCase

from .models import Schedule, Suite


class SuiteForm(forms.ModelForm):
    test_cases = forms.ModelMultipleChoiceField(queryset=TestCase.objects.none(), required=False)

    class Meta:
        model = Suite
        fields = ["name", "slug", "description", "retries", "parallelism", "default_environment", "tags"]

    def __init__(self, *args, **kwargs):
        project = kwargs.pop("project", None)
        super().__init__(*args, **kwargs)
        if project:
            self.fields["default_environment"].queryset = project.environments.all()
            self.fields["test_cases"].queryset = project.test_cases.all()
        for field in self.fields.values():
            field.widget.attrs.setdefault(
                "class",
                "w-full rounded-lg border border-slate-200 dark:border-slate-700 bg-white/80 dark:bg-slate-900/60 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500",
            )
        self.fields["slug"].required = False

    def save(self, commit: bool = True):
        suite = super().save(commit=commit)
        test_cases = self.cleaned_data.get("test_cases")
        if test_cases is not None:
            suite.suite_tests.all().delete()
            for index, test in enumerate(test_cases, start=1):
                suite.suite_tests.create(test_case=test, order=index)
        return suite


class ScheduleForm(forms.ModelForm):
    class Meta:
        model = Schedule
        fields = ["cron", "timezone", "is_active", "human_readable"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault(
                "class",
                "w-full rounded-lg border border-slate-200 dark:border-slate-700 bg-white/80 dark:bg-slate-900/60 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500",
            )
