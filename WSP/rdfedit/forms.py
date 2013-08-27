from django import forms

class DocumentForm(forms.Form):
    docfile = forms.FileField(
        label = 'Select a RDF file to upload end edit',
        #help_text = 'Accepted Formats: XML/RDF, RDF, N3 (not yet implemented)',
    )

class EndpointForm(forms.Form):
    endpoint_url = forms.URLField()

class DeleteForm(forms.Form):
    pass

