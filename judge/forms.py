from django import forms
from django.conf import settings

from .models import Submission


class SubmissionForm(forms.Form):
    language = forms.ChoiceField(choices=Submission.LANGUAGE_CHOICES, initial="cpp")
    source_code = forms.CharField(widget=forms.Textarea)

    def clean_source_code(self):
        code = self.cleaned_data["source_code"]
        if not code.strip():
            raise forms.ValidationError("Source code is empty.")
        if len(code.encode()) > settings.MAX_SOURCE_BYTES:
            raise forms.ValidationError(
                f"Source too large (max {settings.MAX_SOURCE_BYTES // 1024} KB)."
            )
        return code
