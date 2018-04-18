from django.forms import ModelForm, TextInput
from django import forms
import datetime


class CreateCourseForm(forms.Form):
    course_name = forms.CharField(widget=forms.widgets.TextInput)
    course_number = forms.CharField(widget=forms.widgets.TextInput)
    start_date = forms.DateField(initial=datetime.date.today)
    created_date = forms.DateField(initial=datetime.date.today, widget=forms.HiddenInput())
