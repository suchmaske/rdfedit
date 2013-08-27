from django.utils import simplejson
from django.http import HttpResponse
from django.core.servers.basehttp import FileWrapper
from django.utils.encoding import smart_str, smart_unicode

from dajaxice.decorators import dajaxice_register

from WSP.rdfedit.views import getrdf
from WSP.rdfedit.models import RDF_XML, Document
from WSP.rdfedit.spo2rdfjson import spo2rdfjson

from rdflib import Graph, plugin
from rdflib.parser import Parser
from rdflib.serializer import Serializer
from rdflib.namespace import Namespace, NamespaceManager
from rdflib.plugins.serializers.rdfxml import PrettyXMLSerializer

import rdflib
import cStringIO as StringIO

plugin.register("rdf-json", Parser,
   "rdflib_rdfjson.rdfjson_parser", "RdfJsonParser")

namespaces_dict = {
"dc":"http://purl.org/dc/elements/1.1/",
"DOLCE-Lite":"http://www.loa-cnr.it/ontologies/DOLCE-Lite.owl#",
"foaf":"http://xmlns.com/foaf/0.1/",
"ore":"http://www.openarchives.org/ore/terms/",
"dcmitype":"http://purl.org/dc/dcmitype/",
"rdfs":"http://www.w3.org/2000/01/rdf-schema#",
"xsd":"http://www.w3.org/2001/XMLSchema#",
"owl":"http://www.w3.org/2002/07/owl#",
"rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#",
"cidoc_crm_v5":"http://www.cidoc-crm.org/rdfs/cidoc_crm_v5.0.2_english_label.rdfs#",
"core":"http://purl.org/vocab/frbr/core#",
"dcterms":"http://purl.org/dc/terms/",
"skos":"http://www.w3.org/2004/02/skos/core#",
"vs":"http://www.w3.org/2003/06/sw-vocab-status/ns#",
"gnd":"http://d-nb.info/standards/elementset/gnd#",
"edm":"http://www.europeana.eu/schemas/edm/" }

@dajaxice_register(method = 'POST')
def serialize_graph(request, rdfjson, base):

    editgraph = Graph()
    editgraph.parse(data=rdfjson, format="rdf-json")

    namespace_manager = NamespaceManager(Graph())
    for ns in namespaces_dict:
        namespace_manager.bind(ns, Namespace(namespaces_dict[ns]), override=False)

    editgraph.namespace_manager = namespace_manager

    if base:
        """
        RDFLib Module to insert the base during serialization is buggy. Manual insertion needed
        graphxml_string = editgraph.serialize(format="pretty-xml", base=base)
        """
        graphxml_string = editgraph.serialize(format="pretty-xml").decode('utf-8', 'ignore')
        graphxml_string = graphxml_string.replace('rdf:RDF\n', 'rdf:RDF\n  xml:base="' + base +'"\n')
        print graphxml_string
    else:
        graphxml_string = editgraph.serialize(format="pretty-xml")

    graphxml_to_db = RDF_XML(rdfxml_string = graphxml_string)
    graphxml_to_db.save()

    return simplejson.dumps({'message':graphxml_to_db.id}) 
