var connectionChart;
var locationChart;

function createSeries(data, userId) {
     var series = [{ name: "UE " + userId.toString(), pointWidth: 20,
                dataLabels: {
                    align: 'center',
                    enabled: true,
                    format: "{point.name}"}, data: []}];

    if(data == undefined)
        return;

    for(var i = 0; i < data.length; i++)
    {
        series[0].data.push({x: data[i][0], x2: data[i][1],
            y: 0, name: 'Cell ' + data[i][2].toString()});
    }
    return series;
}

function update(data) {
    var series = connectionChart.series[0];

    var points = [];
    for(var i = 0; i < data.length; i++)
    {
        points.push({x: data[i][0], x2: data[i][1],
            y: 0, name: 'Cell ' + data[i][2].toString()});
    }
    series.setData(points, false, false, true);
    connectionChart.redraw();
}

function initialize(data, userId) {
    var series = createSeries(data["Connections"], userId);
    connectionChart = Highcharts.chart('ueConnectionsChartContainer', {
        chart: {
            type: 'xrange',
            height: 200
        },
        title: {
            text: 'Connected cells over time for user ID: ' + userId.toString()
        },
        xAxis: {
            title: {
                text: 'Time[s]'
            },
        },
        yAxis: {
            visible: false,
            title: {
                text: ''
            },
        },
        legend: {
            enabled: false
        },
        tooltip: {formatter: function() {
                return '<b>' + 'Connected to ' + this.point.name + '</b><br/>'+ ' From ' + Highcharts.numberFormat(this.x, 2) +
                    's to ' + Highcharts.numberFormat(this.x2, 2) + 's';
            }
        },
        series: series

    });



    locationChart = new HeatMapChart('ueLocationsChartContainer', 'Locations', ['Location over time for user id: '+ userId.toString(), ''], [['x', 'm'],['y', 'm'], ['User Location', 's']],[
                    [0.00, '#e9e9ea'],
                    [0.99, '#0098d9'],
                    [1.0, '#ff007b']
                ], [0, undefined], [10,10]);

    try{
        locationChart.drawChart(data["Locations"], cellLocations);
    } catch (err) {
    }


}


/**
 * Initialize all the charts.
 */
$(document).ready(function () {
    searchUserLocationButtonHandler()
});

/**
 * Button handler for simulation start and stop buttons.
 * @param button
 * @param start - Boolean. True for start and false for stop.
 * @param url
 */
function searchUserLocationButtonHandler() {
    var userId = document.getElementById('inputTrackUser').value;
    $.ajax({
     url: "userLocationHistory",
    data: {
        UeID: userId
    },
     type: 'GET',
     success: function (data) {
         var parsed = JSON.parse(data);
         if(connectionChart == undefined) initialize(parsed, userId);
         else update(parsed["Connections"]);
         locationChart.update(parsed, true);
         connectionChart.setTitle({text: 'Connected cells over time for user ID: ' + userId.toString()});
         locationChart.chart.setTitle({text: 'Location over time for user ID: '+ userId.toString()});
     },
     failure: function (data) {
         alert("User NUMBER???? doesn't exist");
         // MAYBE ALERT IN CONTROL PANEL
     }
    });
}