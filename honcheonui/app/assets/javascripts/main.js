// This is a manifest file that'll be compiled into including all the files listed below.
// Add new JavaScript/Coffee code in separate files in this directory and they'll automatically
// be included in the compiled file accessible from http://example.com/assets/application.js
// It's not advisable to add code directly here, but if you do, it'll appear at the bottom of the
// the compiled file.
//
//= require jquery
//= require jquery-ui
//= require jquery_ujs
//= require jquery.layout-1.3.0.rc29.15
//= require jquery.layout.resizePaneAccordions-1.0

var app = {}
$(document).ready( function() {
	/* REQUIRED scripts for layout widget
	 * ************************************************************** */
	var myLayout = $('body').layout({
		spacing_open:			4
	,	spacing_closed:			8
	,	west__size:				200
	,	east__size:				200
		// RESIZE Accordion widget when panes resize
	,	west__onresize:				$.layout.callbacks.resizePaneAccordions
	,	north__resizable:			false
	,	north__spacing_open:		0
	,	north__togglerLength_open:	0
	,	north__size:				50
	,	west__spacing_closed:		2
	,	west__spacing_open:			2
	,	west__togglerLength_open:	200
	,	east__initClosed:			true
	,	east__fxName:				"drop"
	,	east__spacing_closed:		20
	,	east__togglerLength_closed:	20
	,	east__togglerLength_open:	20
	,	east__togglerAlign_closed:	"top"
	,	east__togglerAlign_open:	"top"
	,	east__slideTrigger_open:	"mouseover"
	,	south__size:				150
	,	south__initClosed:			true
	,	south__maxSize:				400
	,	south__slidable:			false
	,	south__spacing_closed:		0
	,	south__spacing_open:		0
	,	south__togglerLength_open:	20
	});

	/* for toolbar on header, toggle 'south' console.
	 * ************************************************************** */
	$("#toggle-console").button({
		icons:  {primary:'ui-icon-alert'}
	}).click(function() {
		myLayout.toggle('south')
	});

	/* for main pane, toggle fullscreen
	 * ************************************************************** */
	$("#toggle-fullscreen").button({
		text: false,
		icons:  {primary:'ui-icon-arrow-4-diag'}
	}).click(function() {
		var options;
		if ($(this).text() === "full") {
			options = {
				label: "min",
				icons: {primary:'ui-icon-arrowthick-1-sw'}
			};
			$.each('north,west'.split(','),
				function(){myLayout.hide(this);});
		} else {
			options = {
				label: "full",
				icons: {primary:'ui-icon-arrow-4-diag'}
			};
			$.each('north,west'.split(','),
				function(){myLayout.open(this);});
		}
		$(this).button("option", options);
		options = null;
	});

	/* for main pane, build tab view.
	 * ************************************************************** */
	var $tabs = $("#tabs").tabs({
		tabTemplate: "<li><a href='#{href}'>#{label}</a> <span class='ui-icon ui-icon-close'>Remove Tab</span></li>",
		add: function(event, ui) {
			$tabs.tabs("select", ui.index);
		},
		/*
		select: function(event, ui) { alert("select:"+ui.panel.innerHTML); },
		load: function(event, ui) { alert("load:"+ui.panel.innerHTML); },
		show: function(event, ui) { ui.panel.innerHTML = ''; },
		*/
		/* remove old content from panel. prevent memory leak. */
		remove: function(event, ui) { ui.panel.innerHTML = ''; },
		spinner: 'Retrieving data...'
	});

	$( "#tabs span.ui-icon-close" ).live( "click", function() {
		var index = $( "li", $tabs ).index( $( this ).parent() );
		$tabs.tabs( "remove", index );
	});

	function add_to_tab(id, label, url) {
		if ($(id).length == 0) { 
			$tabs.tabs("add", id, label);
			var tid = id;	// local variable required for ajax.complete.
			/* do not use tabs's url/load that makes ajax request every-load.
			 * but use external ajax() when only adding a new tab.  */
			$.ajax({
				url: url,
				type: "GET",
				dataType: "html",
				complete: function (req, err) {
					$(tid, $tabs).append(req.responseText);
					tid = null;	// XXX check this variable's scope.
				}
			});
		} else {
			idx = $(".ui-tabs-panel", $tabs).index($(id));
			$tabs.tabs("select", idx);
		}
		label = null;
		id = null;
	}
	app.add_to_tab = add_to_tab;

	/* for sidemenu pane, normal menu button
	 * ************************************************************** */
	$("#sidemenu").accordion({ fillSpace:	true });

	$(".side-menu").button({
		create: function(event, ui) {
			$(".side-menu").removeClass("ui-corner-all");
			$(".side-menu").addClass("hcu-side-button");
		}
	}).click(function() {
		var label = $(this).text();
		var id = label.replace(/ /g, '_').toLowerCase();
		add_to_tab("#tab-" + id, label, $(this).attr("value"));
	});

});
// vim: set ts=4 sw=4:
