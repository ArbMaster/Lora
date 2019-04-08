'use strict';

var map;
var marker = false;

function initMap() {
    var elem = document.getElementById('map');
    map = new google.maps.Map(elem,{
        center: {lat: 41.3275, lng: 19.8187},
        zoom: 15
    });
}

function afterTableDraw(settings){
    $(".locate").click(function(e){
        e.preventDefault();
        
        var latitude  = $($(this).closest('tr').children()[3]).text();
        var longitude = $($(this).closest('tr').children()[4]).text();
        
        if(!(latitude && longitude)){
            return;
        }                    
        var loc = new google.maps.LatLng(latitude,longitude);
        if(marker)
            marker.setMap(null);
        marker = new google.maps.Marker({position: loc, map: map});
        $("#map-modal").dialog("open");
        
    });
}

function createTable(){
    $('#uplinks').DataTable({
        "processing": true,
        "serverSide": true,
        "ajax":{
            url :"/api/table",
            type: "post",
            contentType: "application/json",
            data: function (d) {
                return JSON.stringify(d);
            },
            error: function(){  // error handling
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
                //defaultContent: '<img class="locate" height="32" width="32" src="../static/images/pin.png"/>',
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
        maxHeight : 600,
        resizeStop: function(event, ui) {
            google.maps.event.trigger(map, 'resize')
        },
        open: function(event, ui) {
            google.maps.event.trigger(map, 'resize'); 
        }
    });
    
});
