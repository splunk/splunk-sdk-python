%#template to generate a HTML table from a list of tuples (or list of lists, or tuple of tuples or ...)
<html>
<head>
<title>{{application_name}}{{" -- " if event_name else ""}}{{event_name or ""}}</title> 
<!-- JQUERY -->
<script type="text/javascript" src="https://ajax.googleapis.com/ajax/libs/jquery/1.6.2/jquery.js"></script> 

<!-- JQUERY UI -->
<link href="http://ajax.googleapis.com/ajax/libs/jqueryui/1.8/themes/base/jquery-ui.css" rel="stylesheet" type="text/css"/>
<script src="http://ajax.googleapis.com/ajax/libs/jqueryui/1.8/jquery-ui.js"></script>
<script src="/static/js/jquery.ui.selectmenu.js"></script>
<link href="/static/css/jquery.ui.selectmenu.css" rel="stylesheet" type="text/css"/>

<!-- JQUERY TEMPLATES -->
<script src="http://ajax.microsoft.com/ajax/jquery.templates/beta1/jquery.tmpl.js"></script>

<!-- JQUERY FLOT -->
<script type="text/javascript" src="/static/js/jquery.flot.js"></script>
<script type="text/javascript" src="/static/js/jquery.flot.selection.js"></script>

<!-- JQUERY SHOWLOADING -->
<link href="/static/css/showLoading.css" rel="stylesheet" type="text/css"/>
<script src="/static/js/jquery.showLoading.js"></script>

<!-- DATE FORMATTING -->
<script src="/static/js/date.format.js"></script>

<!-- OUR CSS -->
<link href="/static/css/analytics.css" rel="stylesheet" type="text/css"/>

<!-- TEMPLATES -->
<script id="legendEntryTemplate" type="text/x-jquery-tmpl">
    <input type="checkbox" id="legend-label-${index}" checked/>
    <label for="legend-label-${index}" id="${label}">
        <div>
            <div class="legend-color" style="background-color:${color};"></div>
            <div class="legend-text" style="float:left;">${label}</div>
        </div>
    </label>
</script>

<script id="tooltipTemplate" type="text/x-jquery-tmpl">
    <div id="tooltip">
        <div><div id="tooltip-label">${label}</div>: ${value}</div>
        <div id="tooltip-time">${time}</div>
    </div>
</script>

<!-- LOGIC -->
<script type="text/javascript">
    
    var TimeRange = {
        "Hour": "1h",
        "Day": "1d",
        "Week": "1w",
        "Month": "1mon",
    }

    var TickSize = {
        "Hour": [24, "hour"],
        "Day": [1, "day"],
        "Week": [7, "day"],
        "Month": [15, "day"],
    }

    var TimeFormat = {
        "Hour": "ddd, mmm dS, yyyy, htt",
        "Day": "ddd, mmm dS, yyyy",
        "Week": "ddd, mmm dS, yyyy",
        "Month": "ddd, mmm dS, yyyy",
    }

    var currentTimeKey = "Month";
    var currentTimeRange = TimeRange[currentTimeKey];
    var currentTickSize = TickSize[currentTimeKey];
    var currentTimeFormat = TimeFormat[currentTimeKey]

    var request = function(event_name, property, callback) {
        event_name = event_name || "";
        property = property || "";

        // Show the loading screen
        $("#graph-and-legend").showLoading();
        var req = {
            url: "/api/application/{{application_name}}",
            data: {
                event_name: event_name,
                property: property,
                time_range: currentTimeRange,
            },
            method: "GET", 
            success: function(data) {
                callback(data);
                
                // Now that we're done, we can hide the loading screen
                $("#graph-and-legend").hideLoading();
            },
            error: function(xhr, status, thrown) {
                console.log("error", xhr, status, thrown);
                alert("Error");
                $("#graph-and-legend").hideLoading();
            },
        };

        $.ajax(req);
    }

    var showTooltip = function(x, y, label, value, time) {
        $("#tooltipTemplate").tmpl({label: label, value: value, time: time}).css({
            top: y + 5,
            left: x + 5,
        }).appendTo("body").fadeIn(200);
    }

    var updateGraph = function(data) {
        // The events we need to graph
        var events = data.data;

        // We need to assign each of the events a color
        for(var i = 0; i < events.length; i++) {
            events[i].color = i;
        }
        
        // Our default graph options
        var options = {
                xaxis: { 
                    mode: "time" ,
                    minTickSize: currentTickSize,
                    autoscaleMargin: 0.05,
                },
                yaxis: {
                },
                series: {
                    lines: { show: true },
                    points: { show: true }
                },
                selection: { 
                    mode: "x"
                },
                grid: {
                    hoverable: true,
                    clickable: true,  
                },
                legend: {
                    show: false,
                }
        };

        // Get the graph placeholder
        var graphPlaceholder = $("#graph-placeholder");

        // Plot the initial events
        var plot = $.plot(
            graphPlaceholder, 
            events, 
            options);

        // Save the original zoom
        var zoomed = plot.getAxes();
        
        // Whenever the plot selection changes, this will zoom in
        graphPlaceholder.unbind("plotselected");
        graphPlaceholder.bind("plotselected", function (event, ranges) {
            plot = $.plot(
                        graphPlaceholder, events,
                        $.extend(
                            true, 
                            {},
                            options,
                            {
                              xaxis: { min: ranges.xaxis.from, max: ranges.xaxis.to }
                            }
                        )
                    );
            $("#clearSelection").removeClass("hidden");
        });
 
        // Revert the zoom back to the original settings
        $("#clearSelection").unbind("click");
        $("#clearSelection").click(function () {
            plot.setSelection({xaxis: {from: zoomed.xaxis.min, to: zoomed.xaxis.max }});
            $("#clearSelection").addClass("hidden");
        });

        // When we hover over a point, show a tooltip with the label and value
        var previousPoint = null;
        graphPlaceholder.unbind("plothover");
        graphPlaceholder.bind("plothover", function (event, pos, item) {
            if (item) {
                if (previousPoint != item.dataIndex) {
                    previousPoint = item.dataIndex;
                    
                    $("#tooltip").remove();
                    var label = item.series.label;
                    var count = item.datapoint[1];
                    var date = new Date(item.datapoint[0]);

                    showTooltip(item.pageX, item.pageY, label, count, date.format(currentTimeFormat));
                }
            }
            else {
                $("#tooltip").remove();
                previousPoint = null;            
            }
        });

        // Get the data in the plot, and the legend element
        var data = plot.getData();
        var legend = $("#legend");

        // Clear the legend
        legend.html("");
        legend.removeClass("hidden");

        // For each series, we add it to the legend
        for(var i = 0; i < data.length; i++) {
            var label = data[i].label;
            var color = data[i].color;
            $("#legendEntryTemplate").tmpl({index: i, label: label, color: color}).appendTo(legend);
        }

        // Make it into a buttonset
        legend.buttonset();

        legend.unbind("click");
        legend.click(function() {
            // When any series button is clicked, we will loop over all
            // the selected series, and display them
            var newData = [];
            $('#legend').find('label.ui-state-active').each(function() {
                label = $(this).attr("id").trim();
                
                for(var i = 0; i < events.length; i++) {
                    if (events[i].label.trim() === label) {
                        newData.push(events[i]);
                    }
                }
            }); 

            // Set the data and redraw
            plot.setData(newData);
            plot.setupGrid();
            plot.draw();
        });
    };

    var updatePage = function(data) {
        if (data.event_name) {
            // We need to show and set the event info and the property list,
            // Since we now have an event
            $("#event-title-name").text(data.event_name);
            $("#event-title").removeClass("hidden");
            $("#properties-accordion").removeClass("hidden");

            // Since the properties are now visible, we need to set it up
            var propertyChoices = $("#property-choices").buttonset();

            // Unbind any previous events
            propertyChoices.unbind("change");

            // And rebind
            propertyChoices.change(function() {
                $('#property-choices').find('label.ui-state-active').each(function() {
                    property = $(this).attr("id").replace("radio-","").trim();
            
                    if (property !== (data.property_name ? data.property_name : "").trim()) {                
                        request(data.event_name, property, updateAll); 
                    }
                });
            });

            // And we can enable the properties accordion
            $("#properties-accordion").accordion({collapsible: true});
        }
        else {
            // We need to hide the event title and the event accordion
            $("#event-title").addClass("hidden");
            $("#properties-accordion").addClass("hidden");
        }

        if (data.property_name) {
            // We need to show and set the property title,
            // since we have a property selected
            $("#property-title-name").text(data.property_name);
            $("#property-title").removeClass("hidden");

            // Setup the ability to clear the property
            $("#clear-property-link").unbind("click");
            $("#clear-property-link").click(function(e) {
                e.preventDefault();
                $('input[name="radio"]').each(function(t) {
                    this.checked = false;
                });
                request(data.event_name, "", updateAll);
            });
        }
        else {
            // We don't have a property selected, so 
            // time to hide it
            $("#property-title").addClass("hidden");
        }

        // Reset the time-range menu, so we can capture the data
        $('select#time-range').selectmenu({
            style:'dropdown', 
            width: 150,
            maxHeight: 300,
            change: function(e,object) {
                timeValue = object.value;
                currentTimeRange = TimeRange[timeValue];
                currentTickSize = TickSize[timeValue];
                currentTimeFormat = TimeFormat[timeValue];
                request(data.event_name, data.property_name, updateAll);
            },
        });
        $('#time-range-div').removeClass("hidden");
    }

    var updateAll = function(data) {
        updateGraph(data); 
        updatePage(data);
    }

    $(document).ready(function() {
        request("{{event_name}}", "{{property_name}}", updateAll);
    });
</script>
</head>

<body>
<!-- HEADER -->
<div id="header" class="gray-gradient-box">
    <div id="app-title" class="big-title uppercase">
        {{application_name}}
    </div>
    <div id="event-title" class="mini-title hidden">
        Event: <span id="event-title-name"></span>
        <sup>[<a href="{{application_name}}" class="clear-link">clear</a>]</sup>
    </div>
    <div id="property-title" class="mini-title hidden">
        Property: <span id="property-title-name"></span>
        <sup>[<a href="" class="clear-link" id="clear-property-link">clear</a>]</sup>
    </div>

    <!-- TIME RANGE SELECTION MENU -->
    <div id="time-range-div" class="hidden">
        <label for="time-range-options"></label> 
        <select name="time-range-options" id="time-range"> 
            <option value="Hour">Hour</option> 
            <option value="Day">Day</option> 
            <option value="Week">Week</option> 
            <option value="Month" selected="selected">Month</option> 
        </select> 
    </div>
</div>

<!-- GRAPH AND LEGEND -->
<div id="graph-and-legend"> 
    <input id="clearSelection" class="hidden" type="button" value="reset zoom"/>
    <div id="graph-placeholder" class="graph"></div>
    <div id="legend" class="hidden"></div>
</div>


<!-- PROPERTIES -->
<div id="properties-accordion" class="hidden">
    <h3 class="uppercase"><a href="#">properties</a></h3>
    <div>
    <div id="property-choices">
    %for property in properties:
        % name = property["name"]
        <input type="radio" id="radio-{{name}}" name="radio" {{checked if name == property_name else ""}}/>
        <label for="radio-{{name}}" id="radio-{{name}}">{{name}}</label>
    %end
    </div>
    </div>
</div>

<!-- EVENTS -->
<table class="event-table">
<tr class="table-head">
    <th class="table-head-cell center">Event Name</th>
    <th class="table-head-cell center">Event Count</th>
</tr>
%for event in events:
    %name = event["name"]
    %count = event["count"]
  <tr class="event-table-row">
    <td class="event-name-cell"><a href='{{application_name}}?event_name={{name}}'>{{name}}</a></td>
    <td class="event-table-cell">{{count}}</td>
  </tr>
%end
</table>

</body>
</html>