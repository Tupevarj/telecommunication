
/*
    Enables all select regression buttons
 */
function enableSelectRegButton() {
    $("#useSimpleReg").prop('disabled', false);
    $("#useRfReg").prop('disabled', false);
    $("#useSvrReg").prop('disabled', false);
    $("#useDtReg").prop('disabled', false);
}

/*
    Disables all select regression buttons
 */
function disableSelectRegButton() {
    $("#useSimpleReg").prop('disabled', true);
    $("#useRfReg").prop('disabled', true);
    $("#useSvrReg").prop('disabled', true);
    $("#useDtReg").prop('disabled', true);
}

/*
    Change colors of different regression buttons, based on id.
 */
function toggleRegressionButtons(buttonID) {
    // TODO: NOT TO DO LIKE THIS
    if(buttonID == 0) {
       // $("#useSimpleReg").css({background:'#35d1ff', borderColor:'#35d1ff'});
        $("#useSimpleReg").css({background:'#337ab7', borderColor:'#337ab7'});
        $("#useRfReg").css({background:'#9aabb7', borderColor:'#9aabb7'});
        $("#useSvrReg").css({background:'#9aabb7', borderColor:'#9aabb7'});
        $("#useDtReg").css({background:'#9aabb7', borderColor:'#9aabb7'});
    }
    else if(buttonID == 1) {
        $("#useRfReg").css({background:'#337ab7', borderColor:'#337ab7'});
        $("#useSimpleReg").css({background:'#9aabb7', borderColor:'#9aabb7'});
        $("#useSvrReg").css({background:'#9aabb7', borderColor:'#9aabb7'});
        $("#useDtReg").css({background:'#9aabb7', borderColor:'#9aabb7'});
    }
    else if(buttonID == 2) {
        $("#useSvrReg").css({background:'#337ab7', borderColor:'#337ab7'});
        $("#useSimpleReg").css({background:'#9aabb7', borderColor:'#9aabb7'});
        $("#useRfReg").css({background:'#9aabb7', borderColor:'#9aabb7'});
        $("#useDtReg").css({background:'#9aabb7', borderColor:'#9aabb7'});
    }
    else if(buttonID == 3) {
        $("#useDtReg").css({background:'#337ab7', borderColor:'#337ab7'});
        $("#useSimpleReg").css({background:'#9aabb7', borderColor:'#9aabb7'});
        $("#useSvrReg").css({background:'#9aabb7', borderColor:'#9aabb7'});
        $("#useRfReg").css({background:'#9aabb7', borderColor:'#9aabb7'});
    }
}

/*
    Select Decision Tree regression button:
    - Changes button colors accordingly to selection
    - Updates Z-score reference values
 */
$("#useDtReg").click(function () {
     $.ajax({
         url: "selectRegressionModel",
         data: {
            selectedReg: 1,
          },
         type: 'GET',
           beforeSend: function() {
             toggleRegressionButtons(3)
           },
         success: function (data) {
             redrawZscoresChart(data, "Decision Tree Regression");
         },
         failure: function (data) {
             alert("Error at selection regression");
         }
     });
 });

/*
    Select SVR regression button:
    - Changes button colors accordingly to selection
    - Updates Z-score reference values
 */
$("#useSvrReg").click(function () {
     $.ajax({
         url: "selectRegressionModel",
         data: {
            selectedReg: 3,
          },
         type: 'GET',
           beforeSend: function() {
             toggleRegressionButtons(2)
           },
         success: function (data) {
             redrawZscoresChart(data, "SVR Regression");
         },
         failure: function (data) {
             alert("Error at selection regression");
         }
     });
 });


/*
    Select Random Forest regression button:
    - Changes button colors accordingly to selection
    - Updates Z-score reference values
 */
$("#useRfReg").click(function () {
     $.ajax({
         url: "selectRegressionModel",
         data: {
            selectedReg: 2,
          },
         type: 'GET',
           beforeSend: function() {
             toggleRegressionButtons(1)
           },
         success: function (data) {
             redrawZscoresChart(data, "Random Forest Regression");
         },
         failure: function (data) {
             alert("Error at selection regression");
         }
     });
 });

/*
    Select Simple regression button:
    - Changes button colors accordingly to selection
    - Updates Z-score reference values
 */
$("#useSimpleReg").click(function () {
     $.ajax({
         url: "selectRegressionModel",
         data: {
            selectedReg: 0,
          },
         type: 'GET',
           beforeSend: function() {
             toggleRegressionButtons(0)
           },
         success: function (data) {
             redrawZscoresChart(data, "Simple Regression");
         },
         failure: function (data) {
             alert("Error at selection regression");
         }
     });
 });


/*
    Disables all ML training phase buttons
 */
function disableMlButtons() {
    $("#saveML").prop('disabled', true);
    $("#loadML").prop('disabled', true);
    $("#createML").prop('disabled', true);
}

/*
    Enables all ML training phase buttons
 */
function enableMlButtons() {
    $("#saveML").prop('disabled', false);
    $("#loadML").prop('disabled', false);
    $("#createML").prop('disabled', false);
}

/*
    Save regression model button:
    - Disables other ML training phase buttons
    - Calls "saveMLModels" URL
    - Enables other ML training phase buttons
 */
$("#saveML").click(function () {
     $.ajax({
         url: "saveMLModels",
         type: 'GET',
           beforeSend: function() {
             disableMlButtons()
           },
         success: function (data) {
             var parsed = JSON.parse(data);
             if(parsed == 0) {
                 alert("Models need to be created before saving");
             }
             enableMlButtons();
         },
         failure: function (data) {
             alert("Error at saving models");
             enableMlButtons();
         }
     });
 });

/*
    Load regression model button:
    - Disables other ML training phase buttons
    - Calls "loadMLModels" URL
    - Updates regression charts
    - Enables select regression model buttons
    - Enables other ML training phase buttons
 */
 $("#loadML").click(function () {
     $.ajax({
         url: "loadMLModels",
         type: 'GET',
           beforeSend: function() {
             disableMlButtons()
           },
         success: function (data) {
             var parsed = JSON.parse(data);
             if(parsed == 0) {
                 alert("Couldn't find previously saved models");
             }
             else {
                 var parsed = JSON.parse(data);
                 drawRegressionCharts(parsed);
                 enableSelectRegButton();
                 toggleRegressionButtons(0);
             }
             enableMlButtons();
         },
         failure: function (data) {
             alert("Error at loading models");
             enableMlButtons();
         }
     });
 });

/*
    Create regression model button:
    - Disables other ML training phase buttons
    - Calls "createModels" URL
    - Updates regression charts
    - Enables select regression model buttons
    - Enables other ML training phase buttons
 */
 $("#createML").click(function () {
     $.ajax({
         url: "createModels",
         type: 'GET',
           beforeSend: function() {
             disableMlButtons()
           },
         success: function (data) {
             var parsed = JSON.parse(data);
             drawRegressionCharts(parsed)
             enableMlButtons();
             enableSelectRegButton();
             toggleRegressionButtons(0);
         },
         failure: function (data) {
             alert("Error at updating regression charts");
             enableMlButtons();

         }
     });
 });
