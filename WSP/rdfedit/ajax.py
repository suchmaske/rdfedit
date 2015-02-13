from django.http import HttpResponse
from django.core.servers.basehttp import FileWrapper
from django.utils.encoding import smart_str, smart_unicode

from dajaxice.decorators import dajaxice_register

from WSP.rdfedit.views import getrdf
from WSP.rdfedit.models import RDF_XML, Document
from WSP.rdfedit.spo2rdfjson import spo2rdfjson

from WSP.settings import SINDICE_CONFIG_QUERY, SINDICE_CONFIG_MAPPING, SINDICE_API_URL, NAMESPACES_DICT

from rdflib import Graph, plugin, URIRef
from rdflib.parser import Parser
from rdflib.serializer import Serializer
from rdflib.namespace import Namespace, NamespaceManager
from rdflib.plugins.serializers.rdfxml import PrettyXMLSerializer

import rdflib
import cStringIO as StringIO
import urllib2
import json

import django.contrib.staticfiles

plugin.register("rdf-json", Parser,
   "rdflib_rdfjson.rdfjson_parser", "RdfJsonParser")

namespaces_dict = NAMESPACES_DICT

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
        # print graphxml_string
    else:
        graphxml_string = editgraph.serialize(format="pretty-xml")

    graphxml_to_db = RDF_XML(rdfxml_string = graphxml_string)
    graphxml_to_db.save()
    print graphxml_to_db.id

    return json.dumps({'message':graphxml_to_db.id}) 

@dajaxice_register(method = 'POST')
def query_sindice(request, keywords, type, import_config):


    sindice_query = build_sindice_query(keywords, type, import_config["query"])
    
    graph_uris = select_graph(sindice_query, type, import_config["mapping"])
    
    # graph = fetch_triples(sindice_query, type)
    
    #graph_rdfjson = graph.serialize(format="rdf-json")
    
    return json.dumps({"graph_uris": graph_uris})

def build_sindice_query(keywords, type, query_config):
    # Build the basic query
    query = SINDICE_API_URL
    
    # Create a query dictionary
    query_dict = dict()
    
    # Replace the whitespace with +
    query_dict["q"] = keywords.rstrip().replace(" ", "+")
    query_dict["format"] = "json"
    
    # Read the query config
    #query_config = json.loads(open(SINDICE_CONFIG_QUERY, 'r').read())


    if type in query_config:
        type_config = query_config[type]
        
        for parameter in type_config:
            query_dict[parameter] = type_config[parameter]
        
    # Iterable variable
    query_parameters_counter = 0

    # Build the query URL by iterating over the query dict
    for query_parameter in query_dict:
    
        # increment the iterable
        query_parameters_counter += 1
        
        # Adapt the query
        if "=" in query_parameter:
            query += query_parameter + ":" + query_dict[query_parameter]
        else:
            query += query_parameter + "=" + query_dict[query_parameter]
            
        # Add & if appropriate
        if query_parameters_counter < len(query_dict):
            query += "&"
    
    return query

@dajaxice_register(method = 'POST')
def fetch_triples(request, graph_uri, type, query_mapping):
    
    print graph_uri
    
    # Get the mapping
    #query_mapping = json.loads(open(SINDICE_CONFIG_MAPPING, 'r').read())
    
    # Create a new graph
    new_graph = Graph()
    
    # Bind namespaces to the graph
    for ns in namespaces_dict:
        new_graph.bind(ns, Namespace(namespaces_dict[ns]))
    
    if type in query_mapping:
        
        # Get the mapping for the particular type
        type_mapping = query_mapping[type]
        
        # Load the external graph
        external_graph = Graph()
        
        try:
            external_graph.load(URIRef(graph_uri))
        except:
            print "URI unreachable"
        
        for ns in namespaces_dict:
            external_graph.bind(ns, Namespace(namespaces_dict[ns    ]))
        
        # Iterate over the mappings
        for orig_uri in type_mapping:

            # Create a sparql query
            sparql_query = 'select * where { ?s ' + orig_uri +  ' ?o .}'
            
            # Convert the prefix version into a full URIRef
            new_uri_prefix = type_mapping[orig_uri].split(":")[0]
            if new_uri_prefix in namespaces_dict:
                new_uri = URIRef(type_mapping[orig_uri].replace(new_uri_prefix + ":", namespaces_dict[new_uri_prefix]))
                
            for row in external_graph.query(sparql_query):
                #print row
                new_graph.add((row.s, new_uri, row.o))
        
        # Get all triples from the new graph
        triple_list = list()
        spo_query = 'select * where {?s ?p ?o .}'
        for row in new_graph.query(spo_query):
            triple_list.append([row.s, row.p, row.o])
    
        return json.dumps({"triple_list": triple_list})
    
def select_graph(sindice_query, type, query_mapping):
    
    print sindice_query
    
    # Get the mapping
    # query_mapping = import_config["mapping"]
    #query_mapping = json.loads(open(SINDICE_CONFIG_MAPPING, 'r').read())
    
    if type in query_mapping:
        
        # Get the mapping for the particular type
        type_mapping = query_mapping[type]
    
        # Load the request from the query
        request = urllib2.urlopen(sindice_query, None)

        # Parse the result into a json variable
        result = json.loads(request.read())
        
        # Create a new list
        graph_uris = list()
        
        # Add all URIs to the list
        for entry in result["entries"]:
            graph_uris.append(entry["link"])
            
        return graph_uris
    
@dajaxice_register(method = 'POST')
def adaptive_field_query(request, predicate, lit_object, import_config):
    
    predicate = predicate.encode("ascii", 'ignore')
    
    for ns in namespaces_dict:
        
        if predicate.startswith(namespaces_dict[ns]):
            
            predicate = predicate.replace(namespaces_dict[ns], ns + ":")
    

    #query_mapping = json.loads(open(SINDICE_CONFIG_MAPPING, 'r').read())
    query_mapping = import_config["mapping"]

    label_set = set()

    for map_type in query_mapping:

        for key in query_mapping[map_type]:

            if key == predicate or query_mapping[map_type][key] == predicate:

                label_set.add(map_type)

    select_graphs = set()

    for label in label_set:
        sindice_query = build_sindice_query(lit_object, label, import_config["query"])
        graphs = select_graph(sindice_query, label, import_config["mapping"])
        for graph in graphs:
            select_graphs.add(graph)

    select_graphs = list(select_graphs)

    print select_graphs

    return json.dumps({"select_graphs" : select_graphs, "lit_object": lit_object}) 

    """

    # Build a sindice query for that type (predicate) and object
    sindice_query = build_sindice_query(lit_object, predicate)
    
    select_graphs = select_graph(sindice_query, predicate)
    
    
    """
