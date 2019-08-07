'use strict';

var table;

function afterTableDraw(settings){
    $(".locate").click(function(e){
        e.preventDefault();
        var latitude  = $($(this).closest('tr').children()[3]).text();
        var longitude = $($(this).closest('tr').children()[4]).text();
        var data = {'latitude': latitude, 'longitude': longitude}
        $.ajax({
            'url': '/map/',
            'method': 'POST',
            'accepts': 'text/html',
            'contentType': 'application/json',
            'dataType': 'html',
            'data': JSON.stringify(data),
            'success': function(html_data){
                $("#map-modal").html(html_data);
                $("#map-modal").dialog("open");
            },
            'error': function(jqXHR, textStatus, errorThrown){
                $("#map-modal").html("<p>Missing coordinates!</p>");
                $("#map-modal").dialog("open");
            }
        });
        
        
    });
}

function createTable(){
    table = $('#uplinks').DataTable({
        "processing": true,
        "serverSide": true,
        "ajax":{
            url :"/api/table",
            type: "post",
            contentType: "application/json",
            data: function (d) {
                return JSON.stringify(d);
            },
            error: function(jqXHR, textStatus, errorThrown){  // error handling
                console.log("AJAX Error!");
            }
        },
        columns:[
            {data: 'DevEUI'},
            {data: 'Source'},
            {data: 'Time'},
            {data: 'Latitude'},
            {data: 'Longitude'},
            {data: 'UplinkCount'},
            {data: 'UplinkCount'},
            {data: 'Temperature'},
            {
                data: null,
                defaultContent: '<a href="#" class="locate"><i class="fa fa-map-marker"></i></a>',
                searchable: false,
                orderable: false
            }
        ],
        drawCallback: afterTableDraw,
        columnDefs: [
            {"className": "dt-center", "targets": "_all"}
        ],
        searching: false
    });
}

$(document).ready(function(){
    createTable();
    $("#map-modal").dialog({
        autoOpen:false,
        width: 600,
        maxHeight : 600
    });
    
});
