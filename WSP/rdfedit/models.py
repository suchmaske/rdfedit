from django.db import models

#from WSP.rdfedit.filetypevalidator import ContentTypeRestrictedFileField

class Document(models.Model):
    docfile = models.FileField(
        upload_to='documents/%Y',
	)

    def __unicode__(self):
        return str(self.docfile)
 
class RDF_XML(models.Model):
    rdfxml_string = models.TextField()

