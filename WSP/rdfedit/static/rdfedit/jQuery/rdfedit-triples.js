
function js_graph_update(data){
        var temp = data.message;
        var rdf_url = generic_rdfURL.replace(999999, temp);
	window.location.href= rdf_url;
}

function undo() {

	// If the action stack and rdfjson stack are not empty
	if ((rdfjson_stack.length > 0) && (action_stack.length > 0)) {
	
		// Take latest change and revert it
		rdfjson = rdfjson_stack.pop();
		var action = action_stack.pop();
	
		
		if (action["action"] == "add") {
			var del_node = triple_table.fnGetNodes()[action["row"]]
			$(del_node).addClass("deleted");
			window.setTimeout(function() {triple_table.fnDeleteRow(action["row"]);}, 800);
		}

		else if (action["action"] == "delete") {

            triple_table.fnAddData([
                full_to_short_uri(action["subject"]),
                full_to_short_uri(action["predicate"]),
                action["object"]
            ]);

            var new_node = triple_table.fnGetNodes()[triple_table.fnSettings().fnRecordsTotal()-1];
			
			$(new_node).find("td:first-child").attr("uri", short_to_full_uri(action["subject"]));
			$(new_node).find("td:first-child").attr("id", "subject");
			
			$(new_node).find("td:nth-child(2)").attr("uri", short_to_full_uri(action["predicate"]));
			$(new_node).find("td:nth-child(2)").attr("rel","tooltip");
			$(new_node).find("td:nth-child(2)").attr("title", short_to_full_uri(action["predicate"]));
			$(new_node).find("td:nth-child(2)").attr("id","predicate");
			
			console.log($(new_node).html());
			
            triple_table.fnDisplayRow(new_node);
            $(new_node).addClass("added");
            window.setTimeout(function() {$(new_node).removeClass("added");}, 800);

		}

		else if (action["action"] == "update") {

			triple_table.fnUpdate(action["stock_object_container"], action["pos"][0], action["pos"][1], action["pos"][2]);

		}

	}
}


function delete_triple(row, del_obj){
// Delete a selected triple

	// Create a clone of the rdfjson variable 
	var temp_rdfjson = $.extend(true, {}, rdfjson)
	rdfjson_stack.push(temp_rdfjson);

	// Obtain row number
	var del_row = triple_table.fnGetPosition(row);

	// Get subject content
	var del_subject = triple_table.fnGetData(del_row[0], 0, 0);
	del_subject = short_to_full_uri(del_subject);
	console.log("DEL_S: " + Object.keys(rdfjson[del_subject]).length);
	
	// Get predicate content
	var del_predicate = triple_table.fnGetData(del_row[0], 1, 1);
	del_predicate = short_to_full_uri(del_predicate);
	
	// Get object content
    var del_object_container = triple_table.fnGetData(del_row[0], 2, 2);

	// Get full object URI and object type (for rdfjson use)
	var del_object = short_to_full_uri(del_obj);
	var del_object_type = object_type(del_object);

	var del_triple = triple_table.fnGetNodes()[del_row[0]]
	
	// Push to action stack for later undoing
	var action = {"action": "delete", "subject":del_subject, "predicate":del_predicate, "object":del_object_container};
	action_stack.push(action);	
	
	// Delete triple from the rdfjson object --> If subject-predicate has multiple objects
	if (rdfjson[del_subject][del_predicate].length > 1){
		var i=0;
		var temp_array = rdfjson[del_subject][del_predicate]
		$.each(temp_array, function(){
			if (this["value"] == del_object) {
				rdfjson[del_subject][del_predicate].splice(i, 1);
			}
			i = i + 1;	
		});
	}
	
	// Delete triple from the rdfjson object --> If subject-predicate has one object
	else if (rdfjson[del_subject][del_predicate].length == 1) {
		delete rdfjson[del_subject][del_predicate];
	}
	
	// Delete the subject if it has no predicates and objects
	if (Object.keys(rdfjson[del_subject]).length == 0) {
		delete rdfjson[del_subject];
	}

	// Finally delete row from datatables object
	var del_node = triple_table.fnGetNodes()[del_row[0]];
	$(del_node).addClass("deleted");
	window.setTimeout(function() {triple_table.fnDeleteRow(del_row[0]);}, 800);
	
	console.log(rdfjson);
	
}


function add_triple(new_subject, new_predicate, new_object){
// Add new triple

	// Read from the add_boxes
	
	/* Check whether triple is valid. Subject and predicate have to be a URI */
	var success = new Boolean(false);
	if ((valid_uri(new_subject) && valid_uri(new_predicate)) == true) {

		// Create a clone of the rdfjson variable
		var temp_rdfjson = $.extend(true, {}, rdfjson);
		rdfjson_stack.push(temp_rdfjson);

		// Assign variable that keeps track whether the triple addition is valid or not
		success = true;
		
		// If the added subject is not already in the subject-autocomplete-array, append it.
		if ($.inArray(new_subject, autocomplete_subject) < 0) {
			autocomplete_subject.push(new_subject);
			$("#add_subject").autocomplete({source: autocomplete_subject});
		}
		
		// If the added predicate is not already in the predicate-autocomplete-array, append it.
		if ($.inArray(new_predicate, autocomplete_predicate) < 0) {
			autocomplete_predicate.push(new_predicate);
			$("#add_predicate").autocomplete({source: autocomplete_predicate});
		}
		
		new_subject = short_to_full_uri(new_subject);
		new_predicate = short_to_full_uri(new_predicate);

		/* Process new_object */
		var new_object_type = "literal";
		if (valid_uri(new_object) == true) {
			new_object_type = "uri";
			new_object = short_to_full_uri(new_object);
		}	

		/* Create new node that will be inserted into the object-column of the new triple-row */

		new_object_container = create_object_container(new_object);

		if (rdfjson.hasOwnProperty(new_subject)) {
		/* If the subject already exists */
			
			if (rdfjson[new_subject].hasOwnProperty(new_predicate)) {
			/* If the subject-predicate tuple already exists */
				rdfjson[new_subject][new_predicate].push({type: new_object_type, value: new_object});
			}

			else {
				rdfjson[new_subject][new_predicate] = [{type: new_object_type, value: new_object}];
			}

		}
	
		else {
		/* If the subject does not already exist */
			new_predicate_json = {};
			new_predicate_json[new_predicate] = [{type: new_object_type, value: new_object}];
			rdfjson[new_subject] = new_predicate_json;

		}
		/* Add data to table */
		triple_table.fnAddData([
			full_to_short_uri(new_subject),
			full_to_short_uri(new_predicate),
			full_to_short_uri(new_object_container),
		]);

		/* Add to action stack */

		var action = {"action":"add", "row": triple_table.fnSettings().fnRecordsTotal()-1};
		action_stack.push(action);
		
		var new_node = triple_table.fnGetNodes()[triple_table.fnSettings().fnRecordsTotal()-1];

		triple_table.fnDisplayRow(new_node);
		
		console.log(rdfjson);

	}	

	function reset_add_button(icon_class, button_class) {
	// Reset the buttons to default style
		$("#add_button i").removeClass(icon_class);
		$("#add_button i").addClass("icon-plus-sign");
		$("#add_button span").text("Add triple");
		$("#add_button").removeClass(button_class);
		$("#add_button").addClass("btn-primary");
		$(new_node).removeClass("added");
	}

	// Implement feedback (buttons, add_boxes)
	$("#add_button i").removeClass("icon-plus-sign");
	$("#add_button").removeClass("btn-primary");
	
	if (success == true) {
		$("#add_button i").addClass("icon-ok-sign");
		$("#add_button span").text("Success");
		$("#add_button").addClass("btn-success");
		$(new_node).addClass("added");
		setTimeout(function() {reset_add_button("icon-ok-sign", "btn-success");}, 800);
		$("#add_triple input").each( function(){
                        this.value = asInitVals_add[$("#add_triple input").index(this)];
                });

	}
	else {
		$("#add_button i").addClass("icon-warning-sign");
		$("#add_button span").text("Failed");
		$("#add_button").addClass("btn-danger");
		setTimeout(function() {reset_add_button("icon-warning-sign", "btn-danger");}, 800);
	}
	
}

function create_object_container(value) {
// Create an object container that keeps the object column style
// Input: Object value (URI or Literal)
// Return: HTML-string

		var new_object_container = $('<span></span>');
		// Create an empty jQuery object to work with

            if (object_type(value) == "literal") {
				var new_object_icon = $('<span id="object_icon-wrapper"><i id="object-icon" class="icon-white icon-ellipsis-horizontal"></i></span>');
            }
            else {
                    var new_object_icon = $('<span id="object-icon-wrapper"><i id="object-icon" class="icon-white icon-globe"></i></span>');
            }

		var new_object_content = $('<span id="object" contentEditable></span>')
                new_object_content.attr("uri", value);
                new_object_content.text(full_to_short_uri(value));

                var new_object_delete_button = $('<span id="delete_triple"></span>');
                var new_object_delete_button_icon = $('<i class="icon-black icon-remove-sign"></i>');
                new_object_delete_button.append(new_object_delete_button_icon);

                new_object_container.append(new_object_icon);
                new_object_container.append(new_object_content);
                new_object_container.append(new_object_delete_button);

		return new_object_container.html()

}

function object_type(value) {
// Check for object type (URI or Literal)
	var type = "literal";
	if (value.match("^(http|https):")) {
		type = "uri";
	}
	return type;
}

function object_icon(node) {
// Check which icon applies
	var value = $(node).parent().siblings("#object").text();
	if (object_type(short_to_full_uri(value)) == "literal") {
		$(node).addClass("icon-ellipsis-horizontal");
	}
	else {
		$(node).addClass("icon-globe");
	}
}

function short_to_full_uri(value) {
// Convert short URIs to full URIs
	var full_uri = value;
	$.each(namespaces_dict, function(ns_prefix, ns_full) {
		if (value.match("^"+ns_prefix+":")) {
			full_uri = value.replace(ns_prefix + ":", ns_full);
		}
	});
	return full_uri;
}

function full_to_short_uri(value) {
// Convert full URIs to short URIs
	var short_uri = value;
	$.each(namespaces_dict, function(ns_prefix, ns_full) {
		if (value.match("^"+ns_full)) {
			short_uri = value.replace(ns_full, ns_prefix + ":");
		}
	});
	return short_uri;
}

function valid_uri(value){
// Check, whether "value" is a valid uri. If it is, return true, else return false
	var valid_uri_val = new Boolean(false);
	if (value.match("^(http|https):")) {
		valid_uri_val = true;
	}
	else {
		$.each(namespaces_dict, function(ns_prefix, ns_full) {
			if (value.match("^"+ns_prefix+":")) {
				valid_uri_val = true;
			}
		});
	}
	return valid_uri_val;
}

function prefix_to_attr_uri(value){
	
	var new_uri = value;
	$.each(namespaces_dict, function(ns_prefix, ns_full) {
		if (new_uri.match('^'+ ns_prefix)){
			new_uri = new_uri.replace(ns_prefix + ':', ns_full);
		}
        });
	return new_uri;
}

function hide_editbox(cell){
// Close edit box and update graph
	if ($(cell).hasClass('edit')){ 
		$(cell).removeClass('edit');
		$(cell).attr('uri', prefix_to_attr_uri(cell.innerHTML));
		update_graph(cell);
	}
}

function show_editbox(cell){
	$('#object').each( function(){
		hide_editbox(this);
	});
	$(cell).addClass('edit');
}


/* AJAX: JSON exhange between JavaScript and Django for updating the graph */

function update_graph(obj){
/* Update existing triples */

	var changed_object = $(obj).attr('uri');
    var subject = $(obj).parent().siblings("#subject").attr('uri');
	var predicate = $(obj).parent().siblings("#predicate").attr('uri');

	var stock_object_container = create_object_container(stock_object);
	var object_container = create_object_container(changed_object);
        var pos = triple_table.fnGetPosition(obj.parentNode);
        triple_table.fnUpdate(object_container, pos[0], pos[1], pos[2]);

	var action = { "action":"update", "stock_object_container":stock_object_container, "pos":pos};

	action_stack.push(action);

    var temp_rdfjson = $.extend(true, {}, rdfjson)
    rdfjson_stack.push(temp_rdfjson);

	for (var i = 0; i < rdfjson[subject][predicate].length; i++) {
		if (rdfjson[subject][predicate][i]['value'] == stock_object){
			rdfjson[subject][predicate][i]['value'] = changed_object;
		}
	}
}

function serialize_graph(){
	Dajaxice.WSP.rdfedit.serialize_graph(js_graph_update, {'rdfjson':JSON.stringify(rdfjson), 'base':base});
}

/* This function initiates the sindice request by calling Django via AJAX */
function fetch_graphs() {
	var keywords = $("#triple_set_keywords").val();
	
	//
	var type = "";
	if ($("#triple_set_type_select_label").text() == "Other") {
		type = $("#triple_set_type_input").val()
	}
	else {
		type = $("#triple_set_type_select_label").text();
	}

	// Empty the graph selector list
	$("#graph_selector").empty();
	$("#graph_selector_label").html('Choose Graph<span class="caret"></span>');
	
	Dajaxice.WSP.rdfedit.query_sindice(implement_fetched_graph_uris, {'keywords': keywords, 'type': type});
}

function fetch_triples(graph_uri) {
	
	//
	var type = "";
	if ($("#triple_set_type_select_label").text() == "Other") {
		type = $("#triple_set_type_input").val()
	}
	else {
		type = $("#triple_set_type_select_label").text();
	}
	
	Dajaxice.WSP.rdfedit.fetch_triples(implement_fetched_triples, {'graph_uri': graph_uri, 'type': type});
	
}

function implement_fetched_graph_uris(data) {
	
	var graph_uris = data.graph_uris;
	var graph_selector = $("#graph_selector");
	
	
	
	$.each(graph_uris, function(index, value) {
		var value_short = full_to_short_uri(value);
		var list_element = $("<li></li>");
		list_element.append($('<a href="#"></a>').val(value_short).html(value_short));
		graph_selector.append(list_element);
	});
}

/* Return function of AJAX query_sindice */
function implement_fetched_triples(data) {
	//var fetched_triples = JSON.parse(data.fetched_triples)
	var fetched_triples = data.triple_list;
	
	for (var i=0; i < fetched_triples.length; i++) {
		
		var current_triple = fetched_triples[i];
		var new_subject = current_triple[0];
		var new_predicate = current_triple[1];
		var new_object = current_triple[2];
		
		add_triple(new_subject, new_predicate, new_object);
	}
}

/* Autocomplete of input fields */

/* Datatables */

var asInitVals = new Array();
asInitVals_add = new Array();
$(document).ready(function() {
	
	predicate_set_short = new Array();

	$.each(predicate_set_full, function() {
		var new_short_uri = full_to_short_uri(this);
		predicate_set_short.push(new_short_uri);
	});

	/* Declare stack_variables */

	rdfjson_stack = new Array();
	action_stack = new Array();

    $("#subject, #predicate, #object").each( function() {
    /* Abbreviate full URIs to prefix-value-pairs */
        var cell = this;
        $.each(namespaces_dict, function(ns_prefix, ns_full) {
            if (cell.innerHTML.match("^"+ns_full)) {
                cell.innerHTML = cell.innerHTML.replace(ns_full, ns_prefix + ':');
            }
        } );
    } );

    $("#object-icon-wrapper #object-icon").each( function() {
        object_icon(this);
    });


	// Initialize DataTable object
    triple_table = $('#triples').dataTable( {
                "sDom": '<"row"<"span7"l><"span8"i>f>rt<"offset6 span6"p>',
                "sPaginationType": "bootstrap",
                "oLanguage": {
                        "sLengthMenu": "_MENU_ records per page"
                },
		"bSortClasses": false,
		"bRetrieve": true
        } );

	// Index default values of the search boxes 
    $("tfoot input").keyup( function () {
        triple_table.fnFilter( this.value, $("tfoot input").index(this) );
    } );

	// Put the default values of the search boxes into an array variable
    $("tfoot input") .each( function (i) {
        asInitVals[i] = this.value;
    } );
	
	// If a search box is clicked on and it contains the default value, the box is emptied.
    $("tfoot input").focus( function() {
        if (this.className == "search_init" ) {
            this.className = "";
            this.value = "";
        }
    } );

	// If the search box is left empty, restore the default value.
    $("tfoot input").blur( function (i) {
        if ( this.value == "" ) {
            this.className = "search_init";
            this.value = asInitVals[$("tfoot input").index(this)];
        }
    } );

	// Index the default values of the add_triple boxes
    $("#add_triple input").each( function(i) {
        asInitVals_add[i] = this.value;
    } );

	// If an add_box is clicked on and it contains the default value, the box is emptied.
    $("#add_triple input").focus( function() {
		
        if ($(this).hasClass("add_init")) {
            $(this).removeClass("add_init");
            $(this).attr("value","");
        }
    } );

	// If an add_box is left empty, restore the default value
    $("#add_triple input").blur( function(i) {
        if ($(this).attr("value") == "") {
            $(this).addClass("add_init");
            $(this).attr("value", asInitVals_add[$("#add_triple input").index(this)]);
        }
    } );

    $.extend( $.fn.dataTableExt.oStdClasses, {
        "sWrapper": "dataTables_wrapper form-inline"
    } );
	
	$(function() {
	// Add autocomplete
		var availableNamespaces = [
			"dc:",
			"DOLCE-Lite:",
			"foaf:",
			"ore:",
			"dcmitype:",
			"rdfs:",
			"xsd:",
			"owl:",
			"rdf:",
			"cidoc_crm_v5:",
			"core:",
			"dcterms:",
			"skos:",
			"vs:",
			"gnd:",
			"edm:",
			"wsp:",
			"dc:",
			"dbpedia:",
			"dbpprop"
		];
		
		autocomplete_subject = availableNamespaces.concat(subject_set);
		autocomplete_predicate = availableNamespaces.concat(predicate_set_short);
		
		
		$("#add_subject").autocomplete({source: autocomplete_subject});
		$("#add_predicate").autocomplete({source: autocomplete_predicate});
		$("#add_object").autocomplete({source: availableNamespaces});
		
		
		$("#triple_set_type").autocomplete({source: triple_fetcher_classes});
			
	});
	
	$("#undo_button, #dropdown_undo").click( function() { undo() });
	
	$("#add_button").click( function() { 
	
		var new_subject = $("#add_subject").val();
	    var new_predicate = $("#add_predicate").val();
		var new_object = $("#add_object").val();
		
		add_triple(new_subject, new_predicate, new_object);
		
	});
	
	$("#rdf_export_button, #dropdown_rdf_export").click( function() { serialize_graph() });
	
	$("#fetch_triple_set_button").click( function() { fetch_graphs() })
	
	$(document).on("mouseover", "#predicate", function() {
		$(this).css("cursor","pointer");
	})
	
	$(document).on("click", "#predicate", function() {
		window.open($(this).attr("uri"), "_newtab");
	})
	
	
	$(document).on("click", "#object", function() {
		show_editbox(this);
		stock_object = $(this).attr("uri");
	});
	
	$(document).on("blur", "#object", function() {
		hide_editbox(this);
	});
	
	$(document).on("click", "#delete_triple", function() {
		delete_triple(this.parentNode, $(this).siblings('#object').text());
	});
	
	$(document).on("mouseover", "#delete_triple", function() {
		$(this).css("cursor","pointer");
	});
	
	// Change the value of the predefined triple_fetcher_classes dropdown and change the main value
	$(document).on("click", "#triple_set_type_select li a", function() {
		var selType = $(this).text();
		$("#triple_set_type_select_label").html(selType + '<span class="caret"></span>');
		
		if (selType == "Other") {
			$("#triple_set_type_input").show();
		}
		
		else {
			$("#triple_set_type_input").hide();
		}
	});
	
	// Change the value of the graph_selector
	$(document).on("click", "#graph_selector li a", function() {
		var selGraph = $(this).text();
		var selType = "";
		
		$("#graph_selector_label").html(selGraph + '<span class="caret"></span>');
		
		var fullGraph = short_to_full_uri(selGraph);
		
		fetch_triples(fullGraph);
		
	});
	
	// Add the triple_fetcher_classes to the dropdown menu
	var fetcher_type_selector = $("#triple_set_type_select")
	$.each(triple_fetcher_classes, function(index, value) {
		var list_element = $("<li></li>");
		list_element.append($('<a href="#"></a>').val(value).html(value));
		fetcher_type_selector.append(list_element);
	});
	

});
