/**
 * Class for toggle buttons. Toggle button can be in two state: ON and OFF and it can
 * also be disabled or enabled. Colors can be specified showing each state.
 */
class ToggleButton {
    /**
     * Constructor for toggle button needs button ID (same as html name starting with '#') and colors
     * specified for each state. Also possible to set different color for button being disabled.
     * @param htmlID - Html name starting with '#'
     * @param colorOn - Color for ON state. In HEX format.
     * @param colorOff - Color for OFF state. In HEX format.
     * @param colorDisabled - Color for button being disabled. In HEX format.
     */
     constructor(htmlID, colorOn, colorOff, colorDisabled = "") {
         this.htmlID = htmlID;
         this.cOn = colorOn;
         this.cOff = colorOff;
         this.cDisable = colorDisabled;
         this.state = 0;
     }

    /**
     * Sets button state to ON.
     */
    on() {
         $(this.htmlID).css({background: this.cOn, borderColor: this.cOn});
         this.state = 1;
     }

    /**
     * Sets button state to OFF.
     */
    off() {
         $(this.htmlID).css({background: this.cOff, borderColor: this.cOff});
         this.state = 0;
     }

    /**
     * Enables button.
     */
     enableButton() {
        $(this.htmlID).prop('disabled', false);
        $(this.htmlID).css({background: this.cOff, borderColor: this.cOff});
     }

    /**
     * Disables button.
     */
    disableButton() {
        //if(this.disable)
         $(this.htmlID).prop('disabled', true);
        if(this.cDisable != "") $(this.htmlID).css({background: this.cDisable, borderColor: this.cDisable});
     }

     switchButton() {
        if(this.state == 0) {
            this.on()
        }
        else {
            this.off()
        }
        return this.state
     }
}

/**
 * Class for toggle button in same group. Can specify toggle actions within it's group.
 */
class ToggleButtonGroup {

    /**
     * Constructor takes already created toggle buttons as parameter.
     * @param toggleButtons - ToggleButtons group members.
     */
     constructor(toggleButtons) {
         this.toggleButtons = {};
         for(var i = 0; i < toggleButtons.length; i++) {
            this.toggleButtons[toggleButtons[i].htmlID] = toggleButtons[i];
         }
     }

    /**
     * Disables on button in group.
     * @param buttonID - Button ID (same as html name starting with '#') of button to be disabled.
     */
     disableButton(buttonID) {
         this.toggleButtons[buttonID].disableButton();
     }

    /**
     * Sets specific button's state to ON, and other buttons states to OFF.
     * @param buttonID - Button ID (same as html name starting with '#') of button to be set ON state.
     */
     buttonOnAndOffOthers(buttonID) {
         for (var key in this.toggleButtons) {
             this.toggleButtons[key].off();
         }
         this.toggleButtons[buttonID].on();
     }

    /**
     * Sets button's state to ON.
     * @param buttonID - Button ID (same as html name starting with '#') of button to be set ON state.
     */
     buttonOn(buttonID) {
         this.toggleButtons[buttonID].on();
     }

    /**
     * Puts button in OFF state.
     * @param buttonID - Button ID (same as html name starting with '#') of button to be set OFF state.
     */
     buttonOff(buttonID) {
         this.toggleButtons[buttonID].off();
     }

    /**
     * Enables other buttons in same group and disables specific button.
     * @param buttonID - Button ID (same as html name starting with '#') of button to be set disabled.
     */
     enableOthers(buttonID) {
         for (var key in this.toggleButtons) {
             this.toggleButtons[key].enableButton();
         }
         this.toggleButtons[buttonID].disableButton();
     }

    /**
     * Disables other buttons in same group and enables specific button.
     * @param buttonID - Button ID (same as html name starting with '#') of button to be set enabled.
     */
     disableOthers(buttonID) {
         for (var key in this.toggleButtons) {
             this.toggleButtons[key].disableButton();
         }
         this.toggleButtons[buttonID].enableButton();
     }

    /**
     * Disables all buttons in group.
     */
    disableAll() {
         for (var key in this.toggleButtons) {
             this.toggleButtons[key].disableButton();
         }
     }

    /**
     * Enables all buttons in group.
     */
    enableAll() {
         for (var key in this.toggleButtons) {
             this.toggleButtons[key].enableButton();
         }
     }

    /**
     * Enables single button.
     * @param buttonID - Button ID (same as html name starting with '#') of button to be set enabled.
     */
     enableButton(buttonID) {
         this.toggleButtons[buttonID].enableButton();
     }
}
