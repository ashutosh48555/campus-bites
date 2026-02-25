from django import forms

from payments.models import Payment
from .models import Feedback


class PickupTimeForm(forms.Form):
    pickup_time = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={"type": "datetime-local"}),
        input_formats=["%Y-%m-%dT%H:%M"],
    )
    payment_method = forms.ChoiceField(choices=Payment.METHOD_CHOICES)


class ExtendPickupTimeForm(forms.Form):
    new_pickup_time = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={"type": "datetime-local"}),
        input_formats=["%Y-%m-%dT%H:%M"],
        label="New Pickup Time"
    )


class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ["rating", "comment"]
        widgets = {
            "rating": forms.RadioSelect(),
            "comment": forms.Textarea(attrs={
                "rows": 4, 
                "placeholder": "Share your experience...",
                "class": "w-full px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500"
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ensure rating field doesn't have empty choice
        self.fields['rating'].required = True
        self.fields['rating'].empty_label = None
