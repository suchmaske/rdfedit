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
	* rdflib-sparql (Install manually)
	* rdflib-rdfjson (Install manually)
	* widget-tweaks https://pypi.python.org/pypi/django-widget-tweaks
	* simplejson https://pypi.python.org/pypi/simplejson/
	* You can download most packages using pip (sudo pip install rdflib)

* jQuery
* Bootstrap CSS
* Font Awesome Icons https://fortawesome.github.io/Font-Awesome/
* Spin.js https://fgnass.github.io/spin.js/

