

// Charts:
var chartTotalThr;
var chartRsrpLine;
var chartRsrpColumn;
var chartRem;
var chartRegression;
var chartSvrRegression;
var chartDtRegression;
var chartRfRegression;
var chartZScoreColumn;
var chartNewZScoreColumn;
var first = true;

//
// function loadTable(tableId, fields, data) {
//     var rows = '';
//     $.each(data, function(index, item) {
//         var row = '<tr>';
//         $.each(fields, function(index, field) {
//                 row += '<td>' + item[field+''] + '</td>';
//             });
//         rows += row + '<tr>';
//     });
//     $('#' + tableId + ' tbody').html(rows);
// }

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
    if(regression.length > 0) drawSimpleRegressionChart(regression);
    if(regressionDt.length > 0) drawDtRegressionChart(regressionDt);
    if(regressionRf.length > 0) drawRfRegressionChart(regressionRf);
    if(regressionSvr.length > 0) drawSvrRegressionChart(regressionSvr);
    if(regressionZScores.length > 0) drawZScoreColumnChart(regressionZScores);

    //document.getElementById("knnadAUC").innerHTML = knAuc;

if(first) {
    setInterval(function () {
        first = false;
        $.get('/updateCharts', function (data) {

           // $('#mlTable').bootstrapTable('refresh', {silent: true});
          //  $('#mlTable').bootstrapTable('refresh', {silent: true});
            if (data.length < 3) return;

            var parsed = JSON.parse(data);

            if (parsed["TotalThroughput"] != undefined) {
                // TODO: REMOVE DOUBLE PARSING (DOUBLE DUMPS)
                var tThr = JSON.parse(parsed["TotalThroughput"]);
                if (chartTotalThr != undefined)
                    updateTotalThroughputChart(tThr, parsed['Initialize'] == 'true');
                else
                    drawTotalThroughputChart(tThr); // Initialize if chart is undefined
            }
            if (parsed["RSRP"] != undefined) {
                var rsrp = JSON.parse(parsed["RSRP"]);
                if (chartRsrpLine != undefined)
                    updateRsrpLineChart(rsrp, parsed['Initialize'] == 'true');
                else
                    drawRsrpLineChart(rsrp);
            }
            if (parsed["RsrpPerCell"] != undefined) {
                var rsrpCell = parsed["RsrpPerCell"];
                if (rsrpCell.length > 0) {
                    if (chartRsrpColumn != undefined)
                        updateRsrpColumnChart(rsrpCell);
                    else
                        drawRsrpColumnChart(rsrpCell);
                }
            }
            if (parsed["DominanceMap"] != undefined) {
                var map = JSON.parse(parsed["DominanceMap"]);
                if (chartRem != undefined)
                    updateRemChart(map);
                else
                    drawRemChart(map);
            }

        });
    }, 2000);

    // setInterval(function ()
    // {
    //       $.get('/updateRegressionChart', function (data) {
    //             // TODO: Check if empty
    //             var parsed = JSON.parse(data);
    //
    //             if (parsed["sRegAUC"] != undefined) {
    //
    //                 document.getElementById("simpleReg").innerHTML = parsed["sRegAUC"].substring(0,4);
    //             }
    //             if (parsed["rfRegAUC"] != undefined) {
    //
    //                 document.getElementById("rfReg").innerHTML = parsed["rfRegAUC"].substring(0,4);
    //             }
    //             if (parsed["svcRegAUC"] != undefined) {
    //
    //                 document.getElementById("svcClass").innerHTML = parsed["svcRegAUC"].substring(0,4);
    //             }
    //             if (parsed["dtRegAUC"] != undefined) {
    //
    //                 document.getElementById("decTree").innerHTML = parsed["dtRegAUC"].substring(0,4);
    //             }
    //
    //             if (parsed["Regression"] != undefined) {
    //               var map = JSON.parse(parsed["Regression"]);
    //               if (chartRegression != undefined)
    //                   drawSimpleRegressionChart(map);
    //               else
    //                   updateSimpleRegressionChart(map);
    //             }
    //             if (parsed["RegressionDT"] != undefined) {
    //               var map = JSON.parse(parsed["RegressionDT"]);
    //               if (chartDtRegression != undefined)
    //                   drawDtRegressionChart(map);
    //               else
    //                   updateDtRegressionChart(map);
    //             }
    //             if (parsed["RegressionRF"] != undefined) {
    //               var map = JSON.parse(parsed["RegressionRF"]);
    //               if (chartRfRegression != undefined)
    //                   drawRfRegressionChart(map);
    //               else
    //                   updateRfRegressionChart(map);
    //             }
    //             if (parsed["RegressionSVR"] != undefined) {
    //               var map = JSON.parse(parsed["RegressionSVR"]);
    //               if (chartSvrRegression != undefined)
    //                   drawSvrRegressionChart(map);
    //               else
    //                   updateSvrRegressionChart(map);
    //             }
    //           //auc = parsed["AUC"];
    //       });
    // }, 30000);
}
});


//////////////////////////////////////////////////////////////
//  UPDATE CHART FUNCTIONS
//////////////////////////////////////////////////////////////

/*
    Updates total throughput chart from dictionary
 */
function updateTotalThroughputChart(dictThr, clean)
{
    // var thrTime = dictThr["time"];
    // var thrTotal = dictThr["throughput"];
    //
    // var series = chartTotalThr.series[0];
    //
    // for(var i = 0; i < thrTime.length; i++)
    // {
    //     series.addPoint([thrTime[i], thrTotal[i]], false, false);
    // }

    var series = chartTotalThr.series[0];
    if(series == undefined || clean)
    {
        drawTotalThroughputChart(dictThr);
    }

    for(var i = 0; i < dictThr.length; i++)
    {
        series.addPoint(dictThr[i], false, false);
    }

    chartTotalThr.redraw();
}


/*
    Updates Regression line chart from list
 */
function updateSimpleRegressionChart(listReg)
{
    var series = chartRegression.series[0];
    series.setData(listReg, false, false, true);
    chartRegression.redraw();
}


/*
    Updates Regression line chart from list
 */
function updateRfRegressionChart(listReg)
{
    var series = chartRfRegression.series[0];
    series.setData(listReg, false, false, true);
    chartRfRegression.redraw();
}


/*
    Updates Regression line chart from list
 */
function updateDtRegressionChart(listReg)
{
    var series = chartDtRegression.series[0];
    series.setData(listReg, false, false, true);
    chartDtRegression.redraw();
}


/*
    Updates Regression line chart from list
 */
function updateSvrRegressionChart(listReg)
{
    var series = chartSvrRegression.series[0];
    series.setData(listReg, false, false, true);
    chartSvrRegression.redraw();
}


/*
    Updates RSRP line chart from dictionary
 */
function updateRsrpLineChart(dictRsrp, clean)
{

    var series = chartRsrpLine.series;

    // Initialize all the series:
    if(series[0] == undefined || clean)
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


/*
    Updates RSRP column chart from dictionary
 */
function updateZScoreColumnChart(listZscores)
{
    var series = chartZScoreColumn.series[0];
    var values = [];
    for(var i = 0; i < listZscores.length; i++)
    {
        values[i] = ["BS " + (i+1).toString(), listZscores[i]];
    }
    series.setData(values, false, false, true);
    chartZScoreColumn.redraw();
}

//////////////////////////////////////////////////////////////
//  INITIALIZE CHART FUNCTIONS
//////////////////////////////////////////////////////////////

function drawZScoreColumnChart(listZscore) {

      var seriesPerCell = [{
        'name': 'Z-Score',
        'data': []
        }];

     for(var i = 0; i < listZscore.length; i++) {
         // let id = i.toString();  // Let is not supported
          seriesPerCell[0].data.push(["BS " + (i+1).toString(), listZscore[i]]);
     }

     chartZScoreColumn = Highcharts.chart("newZScoreChartContainer", {
         chart: {
                 type: 'column',
                width: 800
         },
         title: {
            text: 'Z-score for each Basetation'
         },
         subtitle: {
             text: 'Based on distance from basestations'
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
            pointFormat: '{point.y:.1f} Z-score'
        },
        yAxis: {
        },
        legend: {
            enabled: false
        },
         series: seriesPerCell
     });
}

function drawZScoreColumnChart(listZscore) {

      var seriesPerCell = [{
        'name': 'Z-Score',
        'data': []
        }];

     for(var i = 0; i < listZscore.length; i++) {
         // let id = i.toString();  // Let is not supported
          seriesPerCell[0].data.push(["BS " + (i+1).toString(), listZscore[i]]);
     }

     chartZScoreColumn = Highcharts.chart("zScoreChartContainer", {
         chart: {
                 type: 'column',
                width: 800
         },
         title: {
            text: 'Z-score for each Basetation'
         },
         subtitle: {
             text: 'Based on distance from basestations'
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
            pointFormat: '{point.y:.1f} Z-score'
        },
        yAxis: {
        },
        legend: {
            enabled: false
        },
         series: seriesPerCell
     });
}


/*
    Initialize regression chart
*/
function drawSvrRegressionChart(listreg)
{
    // initialize series
    var series = [];
    series.push({name: "reg", data: []});

    // Create series for Regression plot
    for(var i = 0; i < listreg.length; i++) {
        series[0].data.push([listreg[i][0], listreg[i][1]]);
    }

    chartSvrRegression = Highcharts.chart("regressionSvrChartContainer", {
        chart: {
            width: 500
        },
        title: {
            text: 'SVR Regression Model'
        },
        subtitle: {
             text: 'Detection Performance'
         },
         xAxis: {
             crosshair: true,
             title: {
                 text: "FPR"
             }
         },
         yAxis: {
             title: {
                 text: "TPR"
             },
             max: 1.0
         },
         tooltip: {
            pointFormat: '{point.x:.1f} {point.y:.1f} '
        },
        legend: {
            enabled: false
        },
         series: series
     });
}

/*
    Initialize regression chart
*/
function drawDtRegressionChart(listreg)
{
    // initialize series
    var series = [];
    series.push({name: "reg", data: []});

    // Create series for Regression plot
    for(var i = 0; i < listreg.length; i++) {
        series[0].data.push([listreg[i][0], listreg[i][1]]);
    }

    chartDtRegression = Highcharts.chart("regressionDtChartContainer", {
        chart: {
            width: 500
        },
        title: {
            text: 'Decision Tree Regression Model'
        },
        subtitle: {
             text: 'Detection Performance'
         },
         xAxis: {
             crosshair: true,
             title: {
                 text: "FPR"
             }
         },
         yAxis: {
             title: {
                 text: "TPR"
             },
             max: 1.0
         },
         tooltip: {
            pointFormat: '{point.x:.1f} {point.y:.1f} '
        },
        legend: {
            enabled: false
        },
         series: series
     });
}

/*
    Initialize regression chart
*/
function drawRfRegressionChart(listreg)
{
    // initialize series
    var series = [];
    series.push({name: "reg", data: []});

    // Create series for Regression plot
    for(var i = 0; i < listreg.length; i++) {
        series[0].data.push([listreg[i][0], listreg[i][1]]);
    }

    chartRfRegression = Highcharts.chart("regressionRfChartContainer", {
        chart: {
            width: 500
        },
        title: {
            text: 'Random Forest Regression Model'
        },
        subtitle: {
             text: 'Detection Performance'
         },
         xAxis: {
             crosshair: true,
             title: {
                 text: "FPR"
             }
         },
         yAxis: {
             title: {
                 text: "TPR"
             },
             max: 1.0
         },
         tooltip: {
            pointFormat: '{point.x:.1f} {point.y:.1f} '
        },
        legend: {
            enabled: false
        },
         series: series
     });
}

/*
    Initialize regression chart
*/
function drawSimpleRegressionChart(listreg)
{
    // initialize series
    var series = [];
    series.push({name: "reg", data: []});

    // Create series for Regression plot
    for(var i = 0; i < listreg.length; i++) {
        series[0].data.push([listreg[i][0], listreg[i][1]]);
    }

    chartRegression = Highcharts.chart("regressionChartContainer", {
        chart: {
            width: 500
        },
        title: {
            text: 'Simple Regression Model'
        },
        subtitle: {
             text: 'Detection Performance'
         },
         xAxis: {
             crosshair: true,
             title: {
                 text: "FPR"
             }
         },
         yAxis: {
             title: {
                 text: "TPR"
             },
             max: 1.0
         },
         tooltip: {
            pointFormat: '{point.x:.1f} {point.y:.1f} '
        },
        legend: {
            enabled: false
        },
         series: series
     });
}

/*
    Initialize total throughput chart
*/
function drawTotalThroughputChart(dictThr)
{
    // var thrTime = dictThr["time"];
    // var thrTotal = dictThr["throughput"];
    // var seriesThr = [{ 'name': 'Total throughtput', 'data': [] }];
    //
    // for(var i = 0; i < thrTime.length; i++)
    // {
    //     seriesThr[0].data.push([thrTime[i], thrTotal[i]]);
    // }
    //
    var seriesThr = [{ 'name': 'Total throughtput', 'data': [] }];

    for(var i = 0; i < dictThr.length; i++)
    {
        seriesThr[0].data.push(dictThr[i]);
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
    var numberOfCells = Object.keys(dictRsrp).length;
    for(var i = 1; i < numberOfCells; i++)
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

    for(var i = 3; i < numberOfCells-2; i++)
    {
        chartRsrpLine.series[i-1].setVisible(false, false);
    }
    chartRsrpLine.redraw();
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
                [0.35, '#00d0e6'],
                [0.45, '#00eb8d'],
                [0.6, '#e8f500'],
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

function drawRegressionCharts(parsed) {
     if (parsed["sRegAUC"] != undefined) {

        document.getElementById("simpleReg").innerHTML = parsed["sRegAUC"].substring(0,4);
    }
    if (parsed["rfRegAUC"] != undefined) {

        document.getElementById("rfReg").innerHTML = parsed["rfRegAUC"].substring(0,4);
    }
    if (parsed["svcRegAUC"] != undefined) {

        document.getElementById("svcClass").innerHTML = parsed["svcRegAUC"].substring(0,4);
    }
    if (parsed["dtRegAUC"] != undefined) {

        document.getElementById("decTree").innerHTML = parsed["dtRegAUC"].substring(0,4);
    }

    if (parsed["Regression"] != undefined) {
      var map = JSON.parse(parsed["Regression"]);
      if (chartRegression != undefined)
          updateSimpleRegressionChart(map);
      else
          drawSimpleRegressionChart(map);
    }
    if (parsed["RegressionDT"] != undefined) {
      var map = JSON.parse(parsed["RegressionDT"]);
      if (chartDtRegression != undefined)
          updateDtRegressionChart(map);
      else
          drawDtRegressionChart(map);
    }
    if (parsed["RegressionRF"] != undefined) {
      var map = JSON.parse(parsed["RegressionRF"]);
      if (chartRfRegression != undefined)
          updateRfRegressionChart(map);
      else
          drawRfRegressionChart(map);
    }
    if (parsed["RegressionSVR"] != undefined) {
      var map = JSON.parse(parsed["RegressionSVR"]);
      if (chartSvrRegression != undefined)
          updateSvrRegressionChart(map);
      else
          drawSvrRegressionChart(map);
    }
    if (parsed["ZScores"] != undefined) {
      var map = JSON.parse(parsed["ZScores"]);
      if (chartZScoreColumn != undefined)
          updateZScoreColumnChart(map);
      else
          drawZScoreColumnChart(map);
    }
}