from django.forms import ModelForm
from django import forms
from datetme import date
from vital.models import Virtual_Machine_Type, Course, Virtual_Machine


class CreateCourseForm(forms.Form):
    course_name = forms.CharField(widget=forms.widgets.TextInput)
    course_number = forms.CharField(widget=forms.widgets.TextInput)
    start_date = forms.DateField(widget=forms.DateInput(attrs={'class': 'datepicker'}), initial=date.today)


class CreateVmsForm(forms.Form):
    vm_name = forms.CharField(widget=forms.widgets.TextInput)
    vm_type = forms.ModelChoiceField(queryset=Virtual_Machine_Type.objects.all())


class CreateNetworksForm(forms.Form):
    hub_name = forms.CharField(widget=forms.widgets.TextInput)
    hub_vms = forms.ModelChoiceField(queryset=Virtual_Machine.objects.all())
    vm_iface = forms.CharField(widget=forms.widgets.TextInput)

    def __init__(self, course_id, *args, **kwargs):
        super(CreateNetworksForm, self).__init__(*args, **kwargs)
        self.fields['hub_vms'].queryset = Virtual_Machine.objects.filter(course=course_id)
