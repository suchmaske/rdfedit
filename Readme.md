rdfedit is tool to work with RDF triples in your browser. Just start the Django application (Python 2.7.3, Django 1.5.1) and call the corresponding website in your browser.

This tool was developed by me during a few weeks of my internship at Berlin-Brandenburg Academy of Sciences and Humanities at the Knowledge Store (Wissensspeicher - WSP) project.

With rdfedit you currently can:
* Upload RDF/XML files and edit them (more format compatibilities are in progress)
* Enter a SPARQL-Endpoint-URI and parse a given number of triples
* Export the edited Data as RDF/XML

Prequisites:
* Django 1.5.1
	* Dajaxice http://www.dajaxproject.com/
	* rdflib https://github.com/RDFLib/rdflib
	* rdflib-jsonld https://github.com/RDFLib/rdflib-jsonld
	* rdflib-sparql
	* rdflib-rdfjson 
	* widget-tweaks https://pypi.python.org/pypi/django-widget-tweaks
	* simplejson https://pypi.python.org/pypi/simplejson/
* jQuery
* Bootstrap CSS
* Spin.js https://fgnass.github.io/spin.js/

	

Todo:
* Support more upload formats
* Provide tests and setup files
* Spring cleaning

My example Instance:

// Go to: http://ec2-54-213-21-249.us-west-2.compute.amazonaws.com:8080/rdfedit/index/ and click the example button. (Link does not longer work, since free tier has expired. Moving to another server)
