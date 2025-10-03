from __future__ import annotations

from django import forms

from backend.apps.projects.models import Locator

from .models import Dataset, TestCase, TestStep


class TestCaseForm(forms.ModelForm):
    class Meta:
        model = TestCase
        fields = ["name", "description", "tags", "estimated_duration", "is_active"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault(
                "class",
                "w-full rounded-lg border border-slate-200 dark:border-slate-700 bg-white/80 dark:bg-slate-900/60 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500",
            )
        if "slug" in self.fields:
            self.fields["slug"].required = False


class TestStepForm(forms.ModelForm):
    locator = forms.ModelChoiceField(queryset=Locator.objects.none(), required=False)

    class Meta:
        model = TestStep
        fields = ["order", "action", "locator", "parameters", "assertion"]
        widgets = {
            "parameters": forms.Textarea(attrs={"rows": 2}),
            "assertion": forms.Textarea(attrs={"rows": 2}),
        }

    def __init__(self, project, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["locator"].queryset = project.locators.all()
        for field in self.fields.values():
            field.widget.attrs.setdefault(
                "class",
                "w-full rounded-lg border border-slate-200 dark:border-slate-700 bg-white/80 dark:bg-slate-900/60 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500",
            )


class DatasetForm(forms.ModelForm):
    class Meta:
        model = Dataset
        fields = ["name", "slug", "description", "data"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault(
                "class",
                "w-full rounded-lg border border-slate-200 dark:border-slate-700 bg-white/80 dark:bg-slate-900/60 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500",
            )
        if "slug" in self.fields:
            self.fields["slug"].required = False
