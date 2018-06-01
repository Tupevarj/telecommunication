
//--------------------------------------------------------------------------------------------------------------
//          START: CHART CLASS
//--------------------------------------------------------------------------------------------------------------

/**
 * Graph class for highcharts.
 * - Supports:
 *   - line chart
 *   - column chart
 *   - multiple-series
 *   - single-series
 *   - categories
 */
class Chart {

    /**
     * Constructor for Chart class object.
     * @param titles - Titles in tuple: [title, subtitle].
     * @param axes - Names and units for axes in tuple: [xAxis = [name, unit], yAxis = [name, unit]].
     * @param containerName - Div in html for chart.
     * @param seriesName - Name for data series. If multiple-series, index >= 1 is appended to series name.
     * @param dataName - Key for data variable in update dictionary.
     * @param multiSeries - True if multiple-series. Else false. NOTE, MULTI-SERIES NEED DATA AS DICTIONARY!
     * @param column - True if column chart. Else false, meaning line chart.
     * @param categories - If zero, won't create categories, else if > 0, this number of BS - CellID categories will be created.
     * @param width - Width of the chart. If null, width will be auto.
     */
    constructor(titles, axes, containerName, seriesName, dataName, multiSeries = false, column = false, categories = 0, width = null) {
        this.width = width;
        this.width = null;
        //this.height = height;
        this.title = titles[0];
        this.subtitle = titles[1];
        this.xAxis = axes[0];
        this.yAxis = axes[1];
        this.container = containerName;

        this.seriesName = seriesName;
        this.dataName = dataName;
        this.multiSeries = multiSeries;
        if(column)
            this.type = 'column';
        else
            this.type = 'line';
        if(categories != 0)
            this.createCategories(categories);
        this.drawn = false;
    }

    /**
     * Set charts width and height. Needs to be redrawn to be applied.
     * @param width - Chart width.
     * @param height- Chart height.
     */
    setSize(width = null, height = null) {
        this.width = width;
        this.height = height;
    }

    /**
     * Initialize draw for chart. Creates series to display on graph and draws graph.
     * Chart configurations are set via Graph-class constructor.
     * @param data - Points for charts. Can be multi-series or single series. In case single-series data should be array
     *               of tuples (points). In case of multi-series data should be dictionary.
     */
    drawChart(data) {
        this.drawn = true;
        if(!this.multiSeries)
            this.createSeries(data);
        else
            this.createMultiSeries(data);

        this.chart = Highcharts.chart(this.container, {
            chart: {
                type: this.type,
                width: this.width,
                height: this.height
            },
             title: {
                 text: this.title
             },
             subtitle: {
                 text: this.subtitle
             },
             xAxis: {
              categories: this.categories,
                 crosshair: true,
                 title: {
                     text: this.xAxis[0] + " " + this.xAxis[1]
                 },
                labels: {
                    rotation: 0,
                    style: {
                        fontSize: '13px',
                        fontFamily: 'Verdana, sans-serif'
                    }
                }
             },
             yAxis: {
                 title: {
                     text: this.yAxis[0] + " " + this.yAxis[1]
                 }
             },
            tooltip: {
                pointFormat: '{point.x:.1f} ' + this.xAxis[1] + '  {point.y:.1f} ' + this.yAxis[1]
            },
             legend: {
                 layout: 'vertical',
                 align: 'right',
                 verticalAlign: 'middle'
             },
             series: this.series

         });
    }

    /**
     * Creates single series. Should not be called manually!
     * @param points - Data for series. Needs to be array of tuples.
     */
    createSeries(points) {
        this.series = [{ 'name': this.seriesName, 'data': [] }];

        if(points == undefined)
            return;

        for(var i = 0; i < points.length; i++)
        {
            this.series[0].data.push(points[i]);
        }
    }

    /**
     * Deletes all points from charts series.
     */
    cleanChart() {
        for(var i = 0; i < this.chart.series.length; i++) {
            this.chart.series[i].setData([]);
        }
        this.chart.yAxis[0].isDirty = true;
        this.chart.redraw();
    }

    /**
     * Creates multi-series. Should not be called manually!
     * @param dictionary - Dictionary containing keys and values. DICTIONARY KEYS ARE USED
     * AS SERIES NAMES!
     */
    createMultiSeries(dictionary) {
        this.series = [];
        if(dictionary == undefined)
            return;

        var xKey = Object.keys(dictionary)[0]; // Expecting the first elment be x (if all series use same x-values).
        var xList = dictionary[xKey];


        for(var i = 1; i < Object.keys(dictionary).length; i++)
        {
            var yList = dictionary[Object.keys(dictionary)[i]];

            this.series.push({name: Object.keys(dictionary)[i], data: []});

            for(var j = 0; j < xList.length; j++) {
                this.series[i-1].data.push([xList[j], yList[j]]);
            }
        }
    }

    /**
     * Hides legend from the chart.
     */
    hideLegend() {
        this.chart.legend.group.hide();
        this.chart.legend.box.hide();
        this.chart.legend.display = false;
    }

    setYAxisMax(max) {
        this.chart.yAxis[0].setExtremes(null, max);
    }

    /**
     * Creates categories for BS - CellID combination. Till example, if bsCount = 1,
     * categories "BS1" - ["Cell 1", "Cell 2", "Cell 3"] will be created.
     * @param bsCount - Number of categories to be created.
     */
    createCategories(bsCount) {

        this.categories = [];

        for(var i = 1; i <= bsCount; i++) {
            var start = (i-1) * 3 + 1;
            this.categories.push({name: "BS" + i.toString(), categories: ["Cell " + start.toString(), "Cell " +
                                    (start + 1).toString(), "Cell " + (start + 2).toString()]})
        }
    }

    setCategoriesNames(categories) {
        this.categories = [];
        for(var i = 0; i < categories.length; i++) {
             this.categories.push({name: categories[i]});
        }
    }

    updateMultiSeries(dictionary, clear) {
        var series = this.chart.series;

        var xKey = Object.keys(dictionary)[0]; // Expecting the first elment be x (if all series use same x-values).
        var xList = dictionary[xKey];

        for(var i = 1; i < Object.keys(dictionary).length; i++)
        {
            var serie = series[i-1];
            var yList = dictionary[Object.keys(dictionary)[i]];

             if(clear) {
                 var values = [];
                 for(var j = 0; j < yList.length; j++) {
                    values.push([xList[j], yList[j]]);
                 }
                 serie.setData(values, false, true, true);
             }
             else {
                for(var j = 0; j < yList.length; j++)
                {
                    serie.addPoint([xList[j], yList[j]], false, false);
                }
             }
        }

        this.chart.redraw();
    }

    /**
     * Updates single-series. Either appends with new data, or initializes with new data.
     * @param points - New data. Should be array of tuples (points).
     * @param clear - If true, chart will be initialized with new data, otherwise new data will be appended.
     */
    updateSeries(points, clear) {

        var series = this.chart.series[0];

        if(clear) {
            series.setData(points, false, false, true);
        }
        else {
            for(var i = 0; i < points.length; i++)
            {
                series.addPoint(points[i], false, false);
            }
        }
        this.chart.redraw();
    }

    /**
     * Main update function. This should be called with new data for chart. Checks the type of chart
     * and automatically will update series and redraws chart.
     * @param data - New data for chart.
     */
    update(data, clear = false) {
        if(data == undefined) // Just in case, not needed actually
            return;

        if(!this.drawn) {
            this.drawChart(data[this.dataName]);
        }
        else {
            if ('Initialize' in data) {
                if (data['Initialize'] != undefined && data['Initialize'] == 'true')
                    this.cleanChart();
            }
            if(data[this.dataName] != undefined) {
                if(!this.multiSeries) this.updateSeries(data[this.dataName], (clear |(this.type == 'column')));
                else this.updateMultiSeries(data[this.dataName], (clear |(this.type == 'column')));
            }
        }
    }
}

//--------------------------------------------------------------------------------------------------------------
//          END: CHART CLASS
//--------------------------------------------------------------------------------------------------------------

//module.exports = Chart;