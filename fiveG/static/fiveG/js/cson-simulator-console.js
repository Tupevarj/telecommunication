
//--------------------------------------------------------------------------------------------------------------
//          START: CONSOLE CLASS
//--------------------------------------------------------------------------------------------------------------

class Console {

    constructor(tableId, linesCount) {
        this.nLines = linesCount;
        var table = document.getElementById(tableId);

        this.rows = [];
            this.cells = [];
        for(var i = 0; i < this.nLines ; i++) {

            var row = table.insertRow(0);
            row.style.cssText = "height:20px;";

            this.rows.push(row);

            var cell1 = row.insertCell(0);
            cell1.style.cssText = "border:none;padding:0;width:210px;";
            var cell2 = row.insertCell(1);
            cell2.style.cssText = "border:none;padding:0;text-align:left;";

            this.cells.push([cell1, cell2]);
        }
        this.cells[0][0].style.cssText = "border:none;padding:0;width:210px;color:#55d3fd;font-weight:bold;";
        this.cells[0][1].style.cssText = "border:none;padding:0;text-align:left;color:#55d3fd;font-weight:bold;";
    }

    /**
     * Moves all message to one row up.
     */
    moveMessages() {

        // var color = this.cells[0][0].style.color.split(/(\(|,| )/)
        // var colorRGB = [parseInt(color[2])-50, parseInt(color[6])-50, parseInt(color[10])-50];
        // this.cells[0][0].style.color = "rgb(" + colorRGB[0].toString() + "," +
        //                                          colorRGB[1].toString() + ", " + colorRGB[2].toString() + ")";
        // this.cells[0][1].style.color = "rgb(" + colorRGB[0].toString() + "," +
        //                                          colorRGB[1].toString() + ", " + colorRGB[2].toString() + ")";

        for(var i = this.nLines-1; i > 0; i--) {
              this.cells[i][0].innerHTML = this.cells[i-1][0].innerHTML;
              this.cells[i][1].innerHTML = this.cells[i-1][1].innerHTML;

              this.cells[i][0].style.color = this.cells[i-1][0].style.color;
              this.cells[i][1].style.color = this.cells[i-1][1].style.color;
        }
    }

    /**
     * Moves older messages up and adds new message two last row.
     * @param message - Two columns message as tuple.
     * @param colorRGB - Message text color in RGB format.
     */
    addMessage(message, colorRGB) {
        this.moveMessages();
        this.cells[0][0].innerHTML = message[0];
        this.cells[0][1].innerHTML = message[1];

        // colorRGB[0] += 50;
        // colorRGB[1] += 50;
        // colorRGB[2] += 50;

        this.cells[0][0].style.color = "rgb(" + colorRGB[0].toString() + "," +
                                                 colorRGB[1].toString() + ", " + colorRGB[2].toString() + ")";
        this.cells[0][1].style.color = "rgb(" + colorRGB[0].toString() + "," +
                                                 colorRGB[1].toString() + ", " + colorRGB[2].toString() + ")";
    }
}

//--------------------------------------------------------------------------------------------------------------
//          END: CONSOLE CLASS
//--------------------------------------------------------------------------------------------------------------

//module.exports = Console;
