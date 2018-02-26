
 $("#updateCharts").click(function () {
     $.ajax({
         url: "updateCharts",
         type: 'GET',
         success: function (data) {
                var parsed = JSON.parse(data);

                // TODO: REMOVE DOUBLE PARSING (DOUBLE DUMPS)
                var tThr = JSON.parse(parsed["TotalThroughput"]);
                var rsrp = JSON.parse(parsed["RSRP"]);
                var rsrpCell = parsed["RsrpPerCell"];

                drawTotalThroughputChart(tThr);
                drawRsrpChart(rsrp);
                drawRsrpColumnChart(rsrpCell);
         },
         failure: function (data) {
             alert("got a error, we are fixing");

         }
     });
 });


 $(document).on("submit", "#controlPanel", function (e) {
     e.preventDefault();
     $.ajax({
         type: $(this).attr("method"),
         url: $(this).attr("action"),
         data: $(this).serialize(),
         success: function (data) {
             $("#alertWarning").addClass("invisible");
             $("#alertSuccess").html(data);
             $("#alertSuccess").removeClass("invisible");
         },
         failure: function (data) {
             $("#alertSuccess").addClass("invisible");
             $("#alertWarning").html(data);
             $("#alertWarning").removeClass("invisible");
         }
     });
 });