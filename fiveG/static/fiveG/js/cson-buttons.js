


var regressionButtons = new ToggleButtonGroup([new ToggleButton("#useSimpleReg_0", '#337ab7', '#9aabb7'), new ToggleButton("#useRfReg_2", '#337ab7', '#9aabb7'),
                                                new ToggleButton("#useSvrReg_3", '#337ab7', '#9aabb7'), new ToggleButton("#useDtReg_1", '#337ab7', '#9aabb7')]);

var regressionModelsButtons = new ToggleButtonGroup([new ToggleButton("#saveML2", '#337ab7', '#337ab7'), new ToggleButton("#loadML2", '#337ab7', '#337ab7'),
                                                new ToggleButton("#createML2", '#337ab7', '#337ab7'), new ToggleButton("#saveML", '#337ab7', '#337ab7'),
                                                new ToggleButton("#loadML", '#337ab7', '#337ab7'), new ToggleButton("#createML", '#337ab7', '#337ab7')]);


var simulatorButtons = new ToggleButtonGroup([new ToggleButton("#startTraining", '#00c815', '#337ab7'), new ToggleButton("#startSimulation", '#00c815', '#337ab7'),
                                                new ToggleButton("#stopSimulation", '#c60005', '#337ab7', '337ab7')]);

var viewButtons = new ToggleButtonGroup([new ToggleButton("#buttonHideML", '#337ab7', '#9aabb7'), new ToggleButton("#buttonHideMon", '#337ab7', '#9aabb7'),
                                                new ToggleButton("#buttonHidePer", '#337ab7', '#9aabb7'), new ToggleButton("#buttonHideEve", '#337ab7', '#9aabb7'),
                                        new ToggleButton("#buttonHideTrack", '#337ab7', '#9aabb7')]);
var outageButton = new ToggleButton("#outageBsButton", "#00C815", '#337ab7');

// Disable stop

/**
 * Toggles between different regression models.
 * Redraws Z-scores chart when regression model is changed.
 * @param button - Enabled button ID.
 */
function regressorButtonHandler(button) {
    $.ajax({
         url: "selectRegressionModel",
         data: {
            selectedReg:  parseInt(button.id.substr(button.id.length - 1)),
          },
         type: 'GET',
           beforeSend: function() {
             regressionButtons.buttonOnAndOffOthers("#" + button.id);
           },
         success: function (data) {
             initializeNetworkMonitoring(data, button.innerText);
         },
         failure: function (data) {
             alert("Error at selection regression");
         }
     });
}

/**
 * ML models creation handler. Will send GET request to server.
 * Based on succession of request will active regression model
 * buttons and show accuracy for different models.
 * @param url - URL for different ML buttons.
 * @param message - Error message for alert.
 * @param draw - Boolean for drawing Z-score chart.
 */
function mlModelsCreationButtonHandler(url, message, draw) {
    $.ajax({
         url: url,
         type: 'GET',
           beforeSend: function() {
             regressionModelsButtons.disableAll();
           },
         success: function (data) {
             var parsed = JSON.parse(data);
             if(parsed == 0) {
                 alert(message);
             }
             else if(draw) {
                var parsed = JSON.parse(data);
                drawRegressionCharts(parsed);
                regressionButtons.enableAll();
                regressionButtons.buttonOnAndOffOthers("#useSimpleReg_0");
             }
             regressionModelsButtons.enableAll();
         },
         failure: function (data) {
             alert("Error at .... models");
             regressionModelsButtons.enableAll();
         }
     });
}

/**
 * Button handler for simulation start and stop buttons.
 * @param button
 * @param start - Boolean. True for start and false for stop.
 * @param url
 */
function simulatorButtonHandler(button, start, url) {
  $.ajax({
     url: url,
     type: 'GET',
       beforeSend: function() {
         if(start) {
             simulatorButtons.buttonOn('#' + button.id);
             simulatorButtons.disableOthers('#stopSimulation');
             simulatorButtons.buttonOn('#stopSimulation');
         }
         else {
             simulatorButtons.buttonOff('#stopSimulation');
            simulatorButtons.enableOthers('#stopSimulation');

         }
       },
     success: function (data) {
         var message = JSON.parse(data);
         document.getElementById('controlPanelMessage').innerHTML = message;
     },
     failure: function (data) {
         alert("Error at updating regression charts");
         regressionModelsButtons.enableAll();
     }
 });
}


function initButtons() {
    $("#stopSimulation").prop('disabled', true);
}


function outageButtonHandler() {
  $.ajax({
        url: "outageInput",
        data: {
            CreateOutage: outageButton.switchButton(),
            BasestationID: document.getElementById('bsOutageId').value,
        },
        type: 'GET',
        beforeSend: function() {
            if(outageButton.state == 1) {
                document.getElementById("bsOutageId").disabled = true;
                document.getElementById("outageBsButton").innerHTML = "Cancel Outage";
            }
            else {
                document.getElementById("bsOutageId").disabled = false;
                document.getElementById("outageBsButton").innerHTML = "Create Outage";
            }
        },
        success: function(data) {
            var responseData = JSON.parse(data);
            document.getElementById("controlPanelMessage").style.color = "green";
            document.getElementById('controlPanelMessage').innerHTML = responseData['Message'];
        }
    });
}


/*
    Handles input through control panel
 */
function sendControlPanelRequest(requestID) {
    $.ajax({
        url: "controlPanelInput",
        data: {
            eventId: requestID,
            bsId: document.getElementById('bsOutageId').value,
        },
        type: 'GET',
        success: function(data) {
            var responseData = JSON.parse(data);
            if (responseData['status'] != 0) {
                document.getElementById("controlPanelMessage").style.color = "red";
            }
            else {
                document.getElementById("controlPanelMessage").style.color = "green";
            }
            document.getElementById('controlPanelMessage').innerHTML = responseData['message'];
        },
        failure: function(data) {
            var message = JSON.parse(data);
            document.getElementById('controlPanelMessage').innerHTML = "ERROR" + message['message'];
        }
    });
}

function hideDivsButtonHandler(button, div) {
    var element = document.getElementById(div);
    if (element.style.display === "none") {
        element.style.display = "block";

        viewButtons.buttonOn('#' + button.id);
    } else {
        element.style.display = "none";
        viewButtons.buttonOff('#' + button.id);
    }

}