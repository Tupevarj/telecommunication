
/*
    DRAW ALL THE CHARTS
 */
var totalThrChart;
drawTotalThroughputChart(throughtputDict);
drawRsrpChart(rsrpDict);
drawRsrpColumnChart(rsrpPerCellList);
drawREM(dominanceMap);
var rsrpChart;


$(document).ready(function(){
    Highcharts.chart({
        chart: {
            renderTo: 'testChartContainer',
            events: {
            load: function () {
                // set up the updating of the chart each second
                var series = this.series[0];
                setInterval(function () {
                    $.get('/updateCharts2',
                        function (data) {


                        var parsed = JSON.parse(data);

                        if(parsed["ThrNew"] != undefined) {
                        // TODO: REMOVE DOUBLE PARSING (DOUBLE DUMPS)
                            var thrs = JSON.parse(parsed["ThrNew"]);
                            var times = thrs["time"];
                            var thrTotal = thrs["throughput"];

                            for(var i = 0; i < times.length; i++) {
                                series.addPoint([times, thrTotal], true, false);
                            }
                        }
                        // if(data.length < 3) return;
                        //
                        // var parsed = JSON.parse(data);
                        //
                        // if(parsed["TotalThroughput"] != undefined) {
                        //     // TODO: REMOVE DOUBLE PARSING (DOUBLE DUMPS)
                        //     var tThr = JSON.parse(parsed["TotalThroughput"]);
                        //     var rsrp = JSON.parse(parsed["RSRP"]);
                        //     var rsrpCell = parsed["RsrpPerCell"];
                        //
                        //     var thrTime = tThr["time"];
                        //     var thrTotal = tThr["throughput"];
                        //
                        //     for(var j = 0; j < thrTime.length; j++) {
                        //         series.addPoint([thrTime[j], thrTotal[j]], true, true);
                        //     }
                        // }

                });
                }, 1000);
            }
        }
        },
         title: {
             text: 'TEST GRAPH'
         },
         subtitle: {
             text: 'used only for testing'
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
         legend: {
             layout: 'vertical',
             align: 'right',
             verticalAlign: 'middle'
         },
         series: [{
            name: 'Total throughtput',
             data: []
         }]

     });
});

function updateTotalThroughputChart(dictThr) {

    var thrTime = dictThr["time"];
    var thrTotal = dictThr["throughput"];

    var series = totalThrChart.series[0];

    for(var i = 0; i < thrTime.length; i++) {
        series.addPoint([thrTime[i], thrTotal[i]], true, false);
    }
}

 function drawTotalThroughputChart(dictThr) {

    var thrTime = dictThr["time"];
    var thrTotal = dictThr["throughput"];

      var seriesThr = [{
        'name': 'Total throughtput',
        'data': []
        }];
     for(var i = 0; i < thrTime.length; i++) {
          seriesThr[0].data.push([thrTime[i], thrTotal[i]]);
     }

    totalThrChart = Highcharts.chart('throughputChartContainer', {
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
         legend: {
             layout: 'vertical',
             align: 'right',
             verticalAlign: 'middle'
         },
         series: seriesThr

     });
 }


function drawRsrpChart(dictRsrp) {

     var rsrpTime = dictRsrp["Time"];

     // Create series for RSRP plot
     var series = [];
     for(i = 1; i < Object.keys(dictRsrp).length; i++) {
         // let id = i.toString();  // Let is not supported
          series.push({
            name: "Cell " + i.toString(),
            data: dictRsrp["RSRP" + i.toString()]
        });
     }

     rsrpChart = Highcharts.chart("rsrpChartContainer", {
          title: {
             text: 'RSRP for each cell'
         },
         subtitle: {
             text: 'Based on average of measurements from each UE'
         },
         xAxis: {
             categories: rsrpTime,
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
         legend: {
             layout: 'vertical',
             align: 'right',
             verticalAlign: 'middle'
         },
         series: series
     });
}


function drawREM(listValues) {

     var listPoints = listValues['Points'];

     // Create series for REM
    // var series = [{
    //     'name': 'x, y, SINR',
    //     'data': [],
    //     'colsize': 16,
    //     'rowsize' : 16
    //     }];

    //series[0].data = listPoints;
     // for(var i = 0; i < listX.length; i++) {
     //       series[0].data.push([listX[i], listY[i], listSinr[i]]);
     //  }

    chartREM = Highcharts.chart('dominanceMapContainer', {

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
                [0, '#2e3436'],
                [0.4, '#57b2dd'],
                [0.7, '#addffa'],
                [1.0, '#EFEFFF']
        ],
        min: -5,
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
        colsize: 8,
        rowsize: 8,
        data: listPoints
    }]
     });
}

function drawRsrpColumnChart(listRsrp) {

      var seriesPerCell = [{
        'name': 'RSRP',
        'data': []
        }];
/*  var seriesPerCell = [{
     'name': 'RSRP',
     'data': [],
     'dataLabels': {
        enabled: true,
        rotation: -90,
        color: '#FFFFFF',
        align: 'right',
        format: '{point.y:.1f}', // one decimal
        y: 10, // 10 pixels down from the top
        style: {
            fontSize: '13px',
            fontFamily: 'Verdana, sans-serif'
                }
     }
 }]; */
     for(i = 0; i < 21; i++) {
         // let id = i.toString();  // Let is not supported
          seriesPerCell[0].data.push(["Cell " + (i+1).toString(), listRsrp[i]]);
     }

     Highcharts.chart("rsrpPerCellChartContainer", {
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



/*
    AUTOMATICALLY UPDATE GRAPHS
 */
$(document).ready(function () {
    setInterval(function () {
        $.get('/updateCharts',
            function (data) {

            if(data.length < 3) return;

            var parsed = JSON.parse(data);

            if(parsed["TotalThroughput"] != undefined) {
                // TODO: REMOVE DOUBLE PARSING (DOUBLE DUMPS)
                var tThr = JSON.parse(parsed["TotalThroughput"]);
                var rsrp = JSON.parse(parsed["RSRP"]);
                var rsrpCell = parsed["RsrpPerCell"];

                // TODO: ONLY ADD POINTS NO FULL RENDER
                updateTotalThroughputChart(tThr);
               // drawTotalThroughputChart(tThr);
                drawRsrpChart(rsrp);
                drawRsrpColumnChart(rsrpCell);
            }
            if(parsed["DominanceMap"] != undefined) {
                var map = JSON.parse(parsed["DominanceMap"]);
                drawREM(map);
            }

            });
        }, 2000);
    });