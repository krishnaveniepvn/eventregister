from django import forms
from .models import Event
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'description', 'venue', 'date', 'capacity', 'price', 'image']
        widgets = {
            'date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'title',
            'description',
            Row(
                Column('venue', css_class='form-group col-md-6'),
                Column('date', css_class='form-group col-md-6'),
                css_class='form-row'
            ),
            Row(
                Column('capacity', css_class='form-group col-md-4'),
                Column('price', css_class='form-group col-md-4'),
                Column('image', css_class='form-group col-md-4'),
                css_class='form-row'
            ),
            Submit('submit', 'Create Event')
        )

class RegistrationForm(forms.Form):
    special_requests = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}), 
        required=False,
        label='Special Requests (Optional)'
    )
    terms_accepted = forms.BooleanField(
        required=True,
        label='I accept the terms and conditions'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'special_requests',
            'terms_accepted',
            Submit('submit', 'Complete Registration')
        )