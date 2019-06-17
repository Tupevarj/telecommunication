

//--------------------------------------------------------------------------------------------------------------
//          START: DOMINANCE MAP CHART CLASS
//--------------------------------------------------------------------------------------------------------------

class HeatMapChart {

    constructor(containerName, dataName, titles, axes, colorStops, colorAxis, pointSize) {
        this.container = containerName;
        this.dataName = dataName;
        this.drawn = false;
        this.title = titles[0];
        this.subtitle = titles[1];
        this.xAxis = axes[0];
        this.yAxis = axes[1];
        this.zAxis = axes[2];
        this.stops = colorStops;
        this.colorAxisMin = colorAxis[0];
        this.colorAxisMax = colorAxis[1];
        this.pointSize = pointSize;
    }

    createSeries(data) {
        var series = [];
        series.push({ name: this.zAxis[0], boostThreshold: 1,
                turboThreshold: 0,
                colsize: this.pointSize[0],
                rowsize: this.pointSize[1],
                data: data});
        return series;
    }

    createMultiSeries(data1, data2) {

        var series = [];
        series.push({ name: this.zAxis[0], boostThreshold: 1,
                turboThreshold: 0,
                colsize: this.pointSize[0],
                rowsize: this.pointSize[1],
                data: data1});

        series.push({ name: 'Cell', boostThreshold: 1,
                dataLabels: { formatter: function() {return 'Cell ' + (this.point.value*10) }, enabled: true, color: '#575557'},
                turboThreshold: 0,
                data: data2});
        return series;

    }
    drawChart(data1, data2 = []) {
        var series = [];
        if(data2.length == 0) {
            series = this.createSeries(data1);
        } else {
            series = this.createMultiSeries(data1, data2);
        }
        this.drawn = true;
        this.chart = Highcharts.chart(this.container, {

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
                text: this.title,
                align: 'center'
            },

            subtitle: {
                text: this.subtitle,
                align: 'center'
            },

            xAxis: {
                title: {
                     text: this.xAxis[0] + " " + '[' + this.xAxis[1] + ']'
                },
                // min: -50,
                //  max: 1050,
                tickInterval: 100
            },

            yAxis: {
                title: {
                     text: this.yAxis[0] + " " + '[' + this.yAxis[1] + ']'
                },
                startOnTick: false,
                endOnTick: false,
                tickWidth: 1,
                // min: -50,
               //   max: 950,
                tickInterval: 100
            },
            legend: {
                align: 'right',
                layout: 'vertical',
                borderWidth: 0,
                verticalAlign: 'middle'
            },
            colorAxis: {
                stops: this.stops,
                min: this.colorAxisMax,
                min: this.colorAxisMin,
                startOnTick: false,
                endOnTick: false,
                labels: {
                    format: '{value}' + this.zAxis[1]
                },
                reversed: false
            },
            tooltip: {
                pointFormat: '{point.x:.1f} ' + this.xAxis[1] + '  {point.y:.1f} ' + this.yAxis[1] + ' {point.value:.2f}' + this.zAxis[1]
            },
            series: series
        });
    }


    update(data, clear = false)
    {
        if(data[this.dataName] != undefined) {
            var points = data[this.dataName];

            if(!this.drawn) {
                this.drawChart(points);
            }
            else {
                var series = this.chart.series[0];
                if(!clear) {
                    for (var i = 0; i < points.length; i++) {
                        series.data[i].value = points[i][2];
                    }
                }
                else {
                    series.setData(points, false, false, true);
                }
                this.chart.yAxis[0].isDirty = true;
                this.chart.redraw();
            }
        }
    }
}

//--------------------------------------------------------------------------------------------------------------
//          END: DOMINANCE MAP CHART CLASS
//--------------------------------------------------------------------------------------------------------------

//module.exports = DominanceMapChart;