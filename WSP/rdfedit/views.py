# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response, get_object_or_404, render
from django.template import RequestContext
from django.template.defaulttags import register
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.core.files import File
from django.core.servers.basehttp import FileWrapper
from django.conf import settings

from dajaxice.core import dajaxice_functions

from WSP.settings import NAMESPACES_DICT, SINDICE_CONFIG_QUERY, SINDICE_CONFIG_MAPPING
from WSP.rdfedit.models import Document, RDF_XML
from WSP.rdfedit.forms import DocumentForm, DeleteForm, EndpointForm
from WSP.rdfedit.spo2rdfjson import spo2rdfjson

from rdflib import Graph, plugin
from rdflib.parser import Parser
from rdflib.serializer import Serializer
from rdflib.namespace import Namespace, NamespaceManager

import os
import cStringIO as StringIO

import json
import sys


reload(sys).setdefaultencoding("utf-8")

"""
Register serializer and parser plugin for correct
interpretation and output of RDFJson and RDF/XML.
"""

plugin.register("rdf-json", Parser,
                "rdflib_rdfjson.rdfjson_parser", "RdfJsonParser")

plugin.register("rdf-json", Serializer,
                "rdflib_rdfjson.rdfjson_serializer", "RdfJsonSerializer")

plugin.register("rdf-json-pretty", Serializer,
                "rdflib_rdfjson.rdfjson_serializer", "PrettyRdfJsonSerializer")


# Create dictionary for namespaces for later bindings and display in the spo-view.
namespaces_dict = NAMESPACES_DICT


def index(request):
    # Handle file upload

    if request.method == 'POST':
        # If upload-button is pressed, upload selected file and display spo-view.
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            newdoc = Document(docfile=request.FILES['docfile'])
            newdoc.save()
            doc_id = newdoc.id

            # Redirect to the document list after POST
            return spo(request, doc_id)

        endpoint_form = EndpointForm(request.POST)
        if endpoint_form.is_valid():
            endpoint_url = request.POST["endpoint_url"]
            return spo(request, endpoint_url)

    else:
        delete(request)
        form = DocumentForm()  # A empty, unbound form
        endpoint_form = EndpointForm()

    # Load documents for the list page
    documents = Document.objects.all()

    # Render list page with the documents and the form
    return render_to_response(
        'rdfedit/index.html',
        {'documents': documents, 'form': form, 'endpoint_form': endpoint_form},
        context_instance=RequestContext(request)
    )


def delete(request):
    # Delete all files that were uploaded by users.
    del_id_list = [doc.id for doc in Document.objects.all()]
    for del_id in del_id_list:
        del_doc = Document.objects.get(pk=del_id)
        if del_id != 1:
            os.remove(os.path.join(settings.MEDIA_ROOT, del_doc.docfile.name))
            del_doc.delete()
    return HttpResponseRedirect(reverse('WSP.rdfedit.views.index'))


def getrdf(doc_id):
    # Load RDF-graph object by document ID in the Database

    doc = Document.objects.get(pk=doc_id)
    graph = Graph()

    if doc.docfile.name.split(".")[-1] == "ttl":
        graph.load(doc.docfile, format="turtle")

    else:
        graph.load(doc.docfile)

    return graph


def newgraph(request):
    print request.method

    # Create and bind namespaces
    namespace_manager = NamespaceManager(Graph())
    for ns in namespaces_dict:
        namespace_manager.bind(ns, Namespace(namespaces_dict[ns]))

    # Create a new graph
    graph = Graph()
    graph.namespace_manager = namespace_manager

    triple_list = []
    subject_list = []
    predicate_list = []

    subject_set = {}
    predicate_set = {}
    object_set = {}

    # Determine xml:base
    subject_base_test_set = {triple[0] for triple in triple_list}
    base_set = {subject[:subject.rfind("/")] for subject in subject_base_test_set}
    # If all subjects share the same substring-base, this substring-base is likely to be the xml:base.
    if len(base_set) == 1:
        base = str(list(base_set)[0]) + "/"
    else:
        base = ""

    # Serialize graph
    rdfjson = graph.serialize(None, format="rdf-json")

    # 
    triple_fetcher_classes = get_triple_fetcher_classes()

    response = render_to_response('rdfedit/triples.html',
                                  {'rdfjson': rdfjson, 'triple_list': triple_list, 'subject_set': subject_set,
                                   'predicate_set': predicate_set, 'object_set': object_set,
                                   'namespaces_dict': json.dumps(namespaces_dict), 'base': base,
                                   'triple_fetcher_classes': triple_fetcher_classes},
                                  context_instance=RequestContext(request))

    return response


def spo(request, doc_id):
    # Create and bind namespaces
    namespace_manager = NamespaceManager(Graph())
    for ns in namespaces_dict:
        namespace_manager.bind(ns, Namespace(namespaces_dict[ns]), override=False)

    # Load graph from the uploaded file

    if type(doc_id) == int or doc_id == "1":
        # If doc_id is an integer, a file was uploaded. If doc_id is the string "1", the example is parsed.

        graph = getrdf(doc_id)
    else:
        # If doc_id is not an integer, therefore a string, an SPARQL-endpoint url is being parsed
        graph = Graph()
        graph.parse(data=spo2rdfjson(doc_id), format="rdf-json")

        # Generate list of triples
    triple_list = []
    subject_list = []
    predicate_list = []
    object_list = []
    for s, p, o in graph:
        triple_list.append([s, p, o])
        subject_list.append(str(s).encode('utf-8', 'ignore'))
        predicate_list.append(str(p).encode('utf-8', 'ignore'))
        # print str(o).encode('utf-8', 'ignore')
        object_list.append(str(o).decode('utf-8', 'ignore'))

    subject_set = json.dumps(list(set(subject_list)))
    predicate_set = json.dumps(list(set(predicate_list)))
    object_set = json.dumps(list(set(object_list)))


    # Determine xml:base
    subject_base_test_set = {triple[0] for triple in triple_list}
    base_set = {subject[:subject.rfind("/")] for subject in subject_base_test_set}
    # If all subjects share the same substring-base, this substring-base is likely to be the xml:base.
    if len(base_set) == 1:
        base = str(list(base_set)[0]) + "/"
    else:
        base = ""

    # Insert namespaces into graph
    graph.namespace_manager = namespace_manager

    triple_fetcher_classes = get_triple_fetcher_classes()

    # Get the config files
    mapping_config = json.loads(open(SINDICE_CONFIG_MAPPING, 'r').read())
    query_config = json.loads(open(SINDICE_CONFIG_QUERY, 'r').read())
    import_label_lengths = dict()

    for tf_class in triple_fetcher_classes:
        mapping_length = len(mapping_config[tf_class])
        query_length = len(query_config[tf_class])

        if mapping_length >= query_length:
            import_label_lengths[tf_class] = mapping_length
        else:
            import_label_lengths[tf_class] = query_length

    import_config = {"query": query_config, "mapping": mapping_config, "import_label_lengths": import_label_lengths}

    import_config_dj = dict()
    for tf_class in triple_fetcher_classes:
        import_config_dj[tf_class] = dict()





    for tf_class in import_config_dj:
        import_config_dj[tf_class]["query"] = dict()
        import_config_dj[tf_class]["mapping"] = dict()


    for tf_class in import_config["query"]:
        i = 0
        for conf in import_config["query"][tf_class]:
            import_config_dj[tf_class]["query"][i] = {conf : import_config["query"][tf_class][conf]}
            i += 1

    for tf_class in import_config["mapping"]:
        i = 0
        for conf in import_config["mapping"][tf_class]:
            import_config_dj[tf_class]["mapping"][i] = {conf : import_config["mapping"][tf_class][conf]}
            i += 1

    print import_config_dj

    # Serialize graph to RDFJson
    rdfjson = graph.serialize(None, format="rdf-json")
    return render_to_response(
        'rdfedit/triples.html',
        {'rdfjson': rdfjson,
         'triple_list': triple_list,
         'subject_set': subject_set,
         'predicate_set': predicate_set,
         'object_set': object_set,
         'namespaces_dict': json.dumps(namespaces_dict),
         'base': base,
         "triple_fetcher_classes": json.dumps(triple_fetcher_classes),
         "import_config": json.dumps(import_config),
         "import_config_dj": import_config_dj},
        context_instance=RequestContext(request)
    )


def rdf(request, rdfxml_id):
    # Get RDF/XML from the database

    rdfxml_object = RDF_XML.objects.get(pk=rdfxml_id)
    rdfxml_string = rdfxml_object.rdfxml_string


    # Create virtual file and write the RDF/XML string into it
    rdfxml_file = StringIO.StringIO()
    rdfxml_file.write(rdfxml_string.encode('utf-8', 'ignore'))

    # Register response as file download
    response = HttpResponse(rdfxml_file.getvalue(), content_type='application/xml')
    response['Content-Disposition'] = 'attachment; filename="rdf.xml"'

    for doc in RDF_XML.objects.all():
        # Make sure the DB stays clean
        doc.delete()

    return response


def get_triple_fetcher_classes():
    # Get available classes for the triple fetcher
    sindice_query_config = json.loads(open(SINDICE_CONFIG_QUERY, 'r').read())
    triple_fetcher_classes = list()

    for triple_fetcher_class in sindice_query_config:
        triple_fetcher_classes.append(triple_fetcher_class)

    return list(set(triple_fetcher_classes))
