
// Charts:
var charts = [];
var mlCharts = [];
var zScoreChart;
var dominanceMapChart;

// Console:
var sim_console;
//var CropOpts = JSON.parse("{{ TotalThroughput | safe }}");


/**
 * Initializes network performance related charts.
 */
function initializePerformanceCharts() {

    charts.push(new Chart(['Network total throughput', '21 cells, 105 users'], [['Time', '[s]'], ['Throughput', '[Mbps]']],
                                        'throughputChartContainer', 'Total throughtput', 'TotalThroughput'));
    charts.push(new Chart(['RSRP for each cell', 'Based on average of measurements from each UE'], [['Time', '[s]'], ['RSRP', '[dB]']],
                                        'rsrpChartContainer', 'Cell ', "RSRP", true));
    charts.push(new Chart(['Current RSRP per cell', 'Based on average of measurements from each UE'], [['',''], ['RSRP', '[dB]']],
                                        'rsrpPerCellChartContainer', 'Cell ', "RsrpPerCell", false, true, 7));
    charts.push(new Chart(['Number of connected users per cell', ''], [['',''], ['UEs','']],
                                        'uesPerCellChartContainer', 'UEs', "UesPerCell", false, true, 7));
    charts.push(new Chart(['RLF per cell', 'Based on average of measurements from each UE'], [['',''], ['RLF', ' count']],
                                        'rlfChartContainer', 'Cell ', "RlfData", false, true, 7));
    charts.push(new Chart(['RLF in whole network', 'Based on average of measurements from each UE'], [['Time', '[s]'], ['RLF', ' count']],
                                        'rlfLineChartContainer', 'RLF in network', "RlfTotal", true));




    // Initialize charts:
    try{
        charts[0].drawChart(throughtputDict);
    } catch (err) {
    }
    try{
        charts[1].drawChart(rsrpDict);
    } catch (err) {
    }
    try{
        charts[2].drawChart(rsrpPerCellList);
    } catch (err) {
    }
    try{
        charts[3].drawChart(uesPerCellDict);
    } catch (err) {
    }
    try{
        charts[4].drawChart(rlfsPerCell);
    } catch (err) {
    }
    try{
        charts[5].drawChart(rlfsTotal);
    } catch (err) {
    }
}

/**
 * Initializes machine learning charts.
 */
function initializeMlCharts() {

    mlCharts.push(new Chart(['SVR Regression Model', 'Detection Performance'], [['FPR', ''], ['TPR', '']],
                                        'regressionSvrChartContainer', '', 'RegressionSVR', false, false, 0, 500));
    mlCharts.push(new Chart(['Random Forest Regression Model', 'Detection Performance'], [['FPR', ''], ['TPR', '']],
                                        'regressionRfChartContainer', '', 'RegressionRF', false, false, 0, 500));
    mlCharts.push(new Chart(['Simple Regression Model', 'Detection Performance'], [['FPR', ''], ['TPR', '']],
                                        'regressionChartContainer', '', 'Regression', false, false, 0, 500));
    mlCharts.push(new Chart(['Decision Tree Regression Model', 'Detection Performance'], [['FPR', ''], ['TPR', '']],
                                        'regressionDtChartContainer', '', 'RegressionDT', false, false, 0, 500));

    zScoreChart = new Chart(['Z-Score For Regressors', 'Based on anomal users in each basestation'], [['Z-score',''], ['','']],
                                            'zScoreChartContainer', '', 'ZScores', true, true);
    zScoreChart.setCategoriesNames(["BS1", "BS2", "BS3", "BS4", "BS5", "BS6", "BS7"]);

    // Initialize machine learning charts
    for(var i = 0; i < mlCharts.length; i++) {
        mlCharts[i].drawChart([]);
        mlCharts[i].hideLegend();
        mlCharts[i].setYAxisMax(1.0);
    }

    // Z score chart in network monitoring
    zScoreChart.setSize(800, 400);
    try{
        zScoreChart.drawChart(regressionZScores);
    } catch (err) {

    }
}


/**
 * Initialize all the charts and console.
 */
$(document).ready(function () {

    initializePerformanceCharts();
    initializeMlCharts();

    sim_console = new Console("consoleTable", 6);

    dominanceMapChart = new HeatMapChart("dominanceMapContainer", "DominanceMap", ['Radio environment map (REM)', 'SINR on z-axis'], [['x', 'm'],['y', 'm'], ['SINR', 'dB']],[
                    [0.15, '#0057bb'], [0.25, '#00d0e6'], [0.35, '#00d0e6'], [0.45, '#00eb8d'], [0.6, '#e8f500'], [0.9, '#ff3700']], [-10,20], [8,8]);
    try{
        dominanceMapChart.drawChart(dominanceMap);
    } catch (err) {
    }

    // Start update loop for charts
    setInterval(function () {
        sendUpdateRequest();
        }, 10000);
});

var last_time_stamp = 0.0;
/**
 * Sends main update request to server and updates charts and simulation console.
 */
function sendUpdateRequest() {
    $.get('/updateCharts', function (data) {

        var parsed = JSON.parse(data);

        for(var i = 0; i < charts.length; i++)
            charts[i].update(parsed);

        // TODO: !!!
        // if(parsed["TotalThroughput"] != undefined) {
        //     var time_curr = parsed["TotalThroughput"][0][0];
        //
        //     if(time_curr > last_time_stamp+0.25){
        //         var ERROR = true;
        //     }
        //     last_time_stamp = parsed["TotalThroughput"][parsed["TotalThroughput"].length-1][0];
        // }

        dominanceMapChart.update(parsed);
        updateSimulationConsole(parsed["SimulationStatus"]);
    });
}

/**
 * Updates simulation console, with status struct conaining message in [0][1] and color in [2].
 * @param status -
 */
function updateSimulationConsole(status) {

    if(status == undefined)
        return;

    for(var i = 0; i < status.length; i++) {

        sim_console.addMessage([status[i][0].replace(/['\"]+/g, ''), status[i][1].replace(/['"]+/g, '')], status[i][2]);
    }
}

/**
 * Updates regression model table and all ML charts. (Called when regression models created or loaded)
 * @param data - Data for table and ML charts.
 */
function drawRegressionCharts(data) {
    document.getElementById("simpleReg").innerHTML = data["sRegAUC"].substring(0,4);
    document.getElementById("rfReg").innerHTML = data["rfRegAUC"].substring(0,4);
    document.getElementById("svcClass").innerHTML = data["svcRegAUC"].substring(0,4);
    document.getElementById("decTree").innerHTML = data["dtRegAUC"].substring(0,4);

    for(var i = 0; i < mlCharts.length; i++)
         mlCharts[i].update(data, true);

    zScoreChart.cleanChart();
    zScoreChart.update(data);
}

/**
 * Redraws Z-score chart clears monitoring table. (Called when selected regression model changes)
 * @param data - Data for charts and monitoring table.
 * @param title - Name of the regressor.
 */
function initializeNetworkMonitoring(data, title) {
    var parsed = JSON.parse(data);
    $('#alarmTable').bootstrapTable({});
    $('#alarmTable').bootstrapTable("removeAll");

    zScoreChart.cleanChart();
    zScoreChart.chart.setTitle({text: "Z-Score for " + title});
    zScoreChart.update(parsed);
}

/**
 * Updates Z-score chart with new Z-scores.
 * @param data - Data for chart.
 */
function updateZscoreChart(data) {
    var parsed = JSON.parse(data);
    zScoreChart.update(parsed);
}

