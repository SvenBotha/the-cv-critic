from django import forms

class CVUploadForm(forms.Form):
    cv = forms.FileField(label='CV', widget=forms.FileInput(attrs={'accept': '.pdf'}))