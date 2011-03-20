%#template to generate a HTML table from a list of tuples (or list of lists, or tuple of tuples or ...)
<html>
<head>

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
<style>

</style>
<title>Splunk Analytics Sample</title>
</head>
<body>
<div id="title">
    <span id="title-text" class="uppercase">Splunk Analytics Sample</span>
</div>
<div id="applications">
%for application in applications:
    <div class="application-info">
        <div class="application-name left">
            <a href='application/{{application["name"]}}'>{{application["name"]}}</a>
        </div>
        <div class="application-event-count right uppercase">
            {{application["count"]}} events
        </div>
    </div>
%end
</div>
</body>
</html>