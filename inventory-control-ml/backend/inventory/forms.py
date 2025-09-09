from django import forms
from .models import Business, Dataset

class DatasetUploadForm(forms.Form):
    name = forms.CharField(
        max_length=100, 
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    description = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        required=False
    )
    file = forms.FileField(
        label="Dataset File",
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Dataset
        fields = ['name', 'description', 'file']

class BusinessForm(forms.ModelForm):
    class Meta:
        model = Business
        fields = ['name', 'industry', 'address', 'contact_email']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'industry': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'contact_email': forms.EmailInput(attrs={'class': 'form-control'}),
        }