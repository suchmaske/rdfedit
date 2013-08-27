from SPARQLWrapper import SPARQLWrapper, JSON
import json, rdflib

rdfjson = {}

def spo2rdfjson(endpoint_url):
    
    sparql = SPARQLWrapper(endpoint_url)
    sparql.setQuery("""
        SELECT *
        WHERE { ?subject ?predicate ?object }
        LIMIT 50
    """)
    
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()

    for triple in results["results"]["bindings"]:
        subject_value = str(triple["subject"]["value"])        
        subject_value.replace(" ","")
        predicate_value = str(triple["predicate"]["value"])
        object_type = str(triple["object"]["type"])
        object_value = str(triple["object"]["value"])

        object_tuple = {"type": object_type, "value": object_value}

        if subject_value in rdfjson:
        
            if predicate_value in rdfjson[subject_value]:

                rdfjson[subject_value][predicate_value].append(object_tuple)

            else:

                rdfjson[subject_value][predicate_value] = [object_tuple]

        else:

            probj = {predicate_value : [object_tuple]}

            rdfjson[subject_value] = probj

        
    return json.dumps(rdfjson) 

