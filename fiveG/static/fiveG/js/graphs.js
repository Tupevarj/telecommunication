

// Charts:
var chartTotalThr;
var chartRsrpLine;
var chartRsrpColumn;
var chartRem;


/*
    Initialize charts and start timer for updating charts
 */
$(document).ready(function ()
{
    // Initialize charts:
    if(Object.keys(throughtputDict).length > 0) drawTotalThroughputChart(throughtputDict);
    if(rsrpDict["Time"].length > 0) drawRsrpLineChart(rsrpDict);
    if(rsrpPerCellList.length > 0) drawRsrpColumnChart(rsrpPerCellList);
    if(dominanceMap["Points"].length > 0) drawRemChart(dominanceMap);

    setInterval(function ()
    {
        $.get('/updateCharts', function (data)
        {
            if(data.length < 3) return;

            var parsed = JSON.parse(data);

            if(parsed["TotalThroughput"] != undefined) {
                // TODO: REMOVE DOUBLE PARSING (DOUBLE DUMPS)
                var tThr = JSON.parse(parsed["TotalThroughput"]);
                if(chartTotalThr != undefined)
                    updateTotalThroughputChart(tThr);
                else
                    drawTotalThroughputChart(tThr); // Initialize if chart is undefined
            }
            if(parsed["RSRP"] != undefined) {
                var rsrp = JSON.parse(parsed["RSRP"]);
                if(chartRsrpLine != undefined)
                    updateRsrpLineChart(rsrp);
                else
                    drawRsrpLineChart(rsrp);
            }
            if(parsed["RsrpPerCell"] != undefined) {
                var rsrpCell = parsed["RsrpPerCell"];
                if(chartRsrpColumn != undefined)
                    updateRsrpColumnChart(rsrpCell);
                else
                    drawRsrpColumnChart(rsrpCell);
            }
            if(parsed["DominanceMap"] != undefined) {
                var map = JSON.parse(parsed["DominanceMap"]);
                if(chartRem != undefined)
                    updateRemChart(map);
                else
                    drawRemChart(map);
            }

        });
    }, 3000);
});

//////////////////////////////////////////////////////////////
//  UPDATE CHART FUNCTIONS
//////////////////////////////////////////////////////////////

/*
    Updates total throughput chart from dictionary
 */
function updateTotalThroughputChart(dictThr)
{
    var thrTime = dictThr["time"];
    var thrTotal = dictThr["throughput"];

    var series = chartTotalThr.series[0];

    for(var i = 0; i < thrTime.length; i++)
    {
        series.addPoint([thrTime[i], thrTotal[i]], false, false);
    }
    chartTotalThr.redraw();
}


/*
    Updates RSRP line chart from dictionary
 */
function updateRsrpLineChart(dictRsrp)
{
    var series = chartRsrpLine.series;

    // Initialize all the series:
    if(series[0] == undefined)
    {
        drawRsrpLineChart(dictRsrp);
    }
    else {
        var rsrpTime = dictRsrp["Time"];

        for(var i = 1; i < Object.keys(dictRsrp).length; i++)
        {
            var ser = series[i-1];
            var cellRsrp = dictRsrp["RSRP" + i.toString()];

            for(var j = 0; j < cellRsrp.length; j++)
            {
                ser.addPoint([rsrpTime[j], cellRsrp[j]], false, false);
            }
        }
        chartRsrpLine.redraw();
    }
}


/*
    Updates RSRP column chart from dictionary
 */
function updateRsrpColumnChart(listRsrp)
{
    var series = chartRsrpColumn.series[0];
    var values = [];
    for(var i = 0; i < listRsrp.length; i++)
    {
        values[i] = ["Cell " + (i+1).toString(), listRsrp[i]];
    }
    series.setData(values, false, false, true);
    chartRsrpColumn.redraw();
}

function updateRemChart(listValues)
{
    var listPoints = listValues["Points"];

    var series = chartRem.series[0];
    for(var j = 0; j < listPoints.length; j++)
    {
       // data.concat(data.map(listValues[j]));
        // series.addPoint(listValues[j], false, false);
        series.data[j].value = listPoints[j][2];
       // series.update({ value: listValues[j][2]}, false);
    }
    chartRem.yAxis[0].isDirty = true;
    chartRem.redraw();

}


//////////////////////////////////////////////////////////////
//  INITIALIZE CHART FUNCTIONS
//////////////////////////////////////////////////////////////

/*
    Initialize total throughput chart
*/
function drawTotalThroughputChart(dictThr)
{
    var thrTime = dictThr["time"];
    var thrTotal = dictThr["throughput"];
    var seriesThr = [{ 'name': 'Total throughtput', 'data': [] }];

    for(var i = 0; i < thrTime.length; i++)
    {
        seriesThr[0].data.push([thrTime[i], thrTotal[i]]);
    }

    chartTotalThr = Highcharts.chart('throughputChartContainer', {
         title: {
             text: 'Network total throughput'
         },
         subtitle: {
             text: '21 cells, 105 users'
         },
         xAxis: {
             crosshair: true,
             title: {
                 text: "Time [s]"
             }
         },
         yAxis: {
             title: {
                 text: 'Throughput [Mbps]'
             }
         },
        tooltip: {
            pointFormat: '{point.x:.1f} s {point.y:.1f} Mbps'
        },
         legend: {
             layout: 'vertical',
             align: 'right',
             verticalAlign: 'middle'
         },
         series: seriesThr

     });
}


/*
    Initialize RSRP line chart
*/
function drawRsrpLineChart(dictRsrp)
{
    var rsrpTime = dictRsrp["Time"];

    // Create series for RSRP plot
    var series = [];
    for(var i = 1; i < Object.keys(dictRsrp).length; i++)
    {
        var rsrps = dictRsrp["RSRP" + i.toString()];
        series.push({name: "Cell " + i.toString(), data: []});

        for(var j = 0; j < rsrpTime.length; j++) {
            series[i-1].data.push([rsrpTime[j], rsrps[j]]);
        }
    }

    chartRsrpLine = Highcharts.chart("rsrpChartContainer", {
        title: {
            text: 'RSRP for each cell'
        },
        subtitle: {
             text: 'Based on average of measurements from each UE'
         },
         xAxis: {
             crosshair: true,
             title: {
                 text: "Time [s]"
             }
         },
         yAxis: {
             title: {
                 text: 'RSRP [dB]'
             }
         },
         tooltip: {
            pointFormat: '{point.x:.1f} s {point.y:.1f} dB'
        },
         legend: {
             layout: 'vertical',
             align: 'right',
             verticalAlign: 'middle'
         },
         series: series
     });
}


function drawRemChart(listValues) {

     var listPoints = listValues['Points'];

    chartRem = Highcharts.chart('dominanceMapContainer', {

    chart: {
        type: 'heatmap',
        margin: [50, 100, 120, 100],
        width: 750,
        height: 570
    },
    boost: {
        useGPUTranslations: true,
        usePreAllocated: true
    },

    title: {
        text: 'Radio environment map (REM)',
        align: 'center'
    },

    subtitle: {
        text: '',
        align: 'center'
    },

    xAxis: {
        title: {
            text: 'x [m]'
        },
        min: -300,
        max: 1300,
        tickInterval: 100

    },

    yAxis: {
        title: {
            text: 'y [m]'
        },
        startOnTick: false,
        endOnTick: false,
        tickWidth: 1,
        min: -300,
        max: 1200,
        tickInterval: 100
    },
    legend: {
        align: 'right',
        layout: 'vertical',
        borderWidth: 0,
        verticalAlign: 'middle'
    },
    colorAxis: {
        stops: [
                [0.35, '#00ddff'],
                [0.45, '#00ff8d'],
                [0.6, '#efff00'],
                [0.9, '#ff3700']
        ],
        min: -10,
        max: 20,
        startOnTick: false,
        endOnTick: false,
        labels: {
            format: '{value}dB'
        },
        reversed: false
    },
    tooltip: {
        pointFormat: '{point.x:.0f} m {point.y:.0f} m {point.value:.2f} dB'
    },
    series: [{
        boostThreshold: 1,
        turboThreshold: 0,
        colsize: 16,
        rowsize: 16,
        data: listPoints
    }]
     });
}


function drawRsrpColumnChart(listRsrp) {

      var seriesPerCell = [{
        'name': 'RSRP',
        'data': []
        }];

     for(var i = 0; i < listRsrp.length; i++) {
         // let id = i.toString();  // Let is not supported
          seriesPerCell[0].data.push(["Cell " + (i+1).toString(), listRsrp[i]]);
     }

     chartRsrpColumn = Highcharts.chart("rsrpPerCellChartContainer", {
         chart: {
                 type: 'column'
         },
         title: {
            text: 'Current RSRP per cell'
         },
         subtitle: {
             text: 'Based on average of measurements from each UE'
         },
         xAxis: {
            type: 'category',
             labels: {
                rotation: -45,
                style: {
                    fontSize: '13px',
                    fontFamily: 'Verdana, sans-serif'
                }
            }
        },
        tooltip: {
            pointFormat: '{point.y:.1f} dB'
        },
        yAxis: {
            max: -50,
            title: {
            text: 'RSRP [dB]'

            }
        },
        legend: {
            enabled: false
        },
         series: seriesPerCell
     });
}

