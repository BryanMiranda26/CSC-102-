#################################
# CSC 102 Defuse the Bomb Project
# Main program
# Team:
#################################
#Import Configs & Phases
from bomb_configs import *
from bomb_phases import *
from PIL import Image, ImageTk
from tkinter import *


###########
# functions
###########
# generates the bootup sequence on the LCD
def bootup(n=0):
    gui._lscroll["text"] = boot_text.replace("\x00", "")
    # configure the remaining GUI widgets
    gui.setup()
    # setup the phase threads, execute them, and check their statuses
    if (RPi):
        setup_phases()
        check_phases()

    # sets up the phase threads

def setup_phases():
    global timer, keypad, wires, button, toggles

    #Rooms
    self.keypad_room = Room(window, "keypad", bg_color="darkblue", bg_image="keypad.png")
    self.wires_room = Room(window, "wires", bg_color="darkgreen", bg_image="wires.png")
    self.button_room = Room(window, "button", bg_color="darkred", bg_image="button.png")
    self.toggles_room = Room(window, "toggles", bg_color="gray", bg_image="toggles.png")
    # setup the timer thread
    timer = Timer(component_7seg, COUNTDOWN)
    # bind the 7-segment display to the LCD GUI so that it can be paused/unpaused from the GUI
    gui.setTimer(timer)
    # setup the keypad thread
    keypad = Keypad(component_keypad, keypad_target)
    # setup the jumper wires thread
    wires = Wires(component_wires, wires_target)
    # setup the pushbutton thread
    button = Button(component_button_state, component_button_RGB, button_target, button_color, timer)
    # bind the pushbutton to the LCD GUI so that its LED can be turned off when we quit
    gui.setButton(button)
    #Show current room
    gui.show_room("keypad")
    # setup the toggle switches thread
    toggles = Toggles(component_toggles, toggles_target)

    # start the phase threads
    timer.start()
    keypad.start()
    wires.start()
    button.start()
    toggles.start()

def check_phases():
    global active_phases
    #Calls the fuse to be displayed
    gui.showFuse(timer._value, COUNTDOWN)
    #adding a visual timer its max value
    gui._timer_bar["maximum"] = COUNTDOWN
    gui._timer_bar["value"] = COUNTDOWN - timer._value
    #Calling the strike marks to represent how many strikes are left
    gui._lstrikes["text"] = f"Strikes left: {'❌' * strikes_left}"
    #Check the current room/phase
    if keypad._running:
        gui.show_room("keypad")
    if wires._running:
        gui.show_room("wires")
    if button._running:
        gui.show_room("button")
    if toggles._running:
        gui.show_room("toggles")
    # check the timer
    if (timer._running):
        # update the GUI
        gui._ltimer["text"] = f"Time left: {timer}"
    else:
        # the countdown has expired -> explode!
        # turn off the bomb and render the conclusion GUI
        turn_off()
        gui.after(100, gui.conclusion, False)
        # don't check any more phases
        return


    if (keypad._running):
    # update the GUI
        gui._lkeypad["text"] = f"Combination: {keypad}"
    # the phase is defused -> stop the thread
    if (keypad._defused):
        keypad._running = False
        active_phases -= 1
    # the phase has failed -> strike
    elif (keypad._failed):
        gui.flashX()
        strike()
        # reset the keypad
        keypad._failed = False
        keypad._value = ""
    # check the wires
    if (wires._running):
    # update the GUI
        gui._lwires["text"] = f"Wires: {wires}"
    # the phase is defused -> stop the thread
    if (wires._defused):
        wires._running = False
        active_phases -= 1
    # the phase has failed -> strike
    elif (wires._failed):
        gui.flashX()
        strike()
        # reset the wires
        wires._failed = False
    # check the button
    if (button._running):
        # update the GUI
        gui._lbutton["text"] = f"Button: {button}"
    # the phase is defused -> stop the thread
    if (button._defused):
        button._running = False
        active_phases -= 1
    # the phase has failed -> strike
    elif (button._failed):
        gui.flashX()
        strike()
        # reset the button
        button._failed = False
    # check the toggles
    if (toggles._running):
        # update the GUI
        gui._ltoggles["text"] = f"Toggles: {toggles}"
    # the phase is defused -> stop the thread
    if (toggles._defused):
        toggles._running = False
        active_phases -= 1
    # the phase has failed -> strike
    elif (toggles._failed):
        gui.flashX()
        strike()
        # reset the toggles
        toggles._failed = False

    # note the strikes on the GUI
    gui._lstrikes["text"] = f"Strikes left: {strikes_left}"
    # too many strikes -> explode!
    if (strikes_left == 0):
        # turn off the bomb and render the conclusion GUI
        turn_off()
        gui.after(1000, gui.conclusion, False)
        # stop checking phases
        return

    # the bomb has been successfully defused!
    if (active_phases == 0):
        # turn off the bomb and render the conclusion GUI
        turn_off()
        gui.after(100, gui.conclusion, True)
        # stop checking phases
        return
    # This allows the phases (e.g. keypad, wires, button, and toggles) text to change colors if the bomb is defused or failed
    # It would stay green if passed or red if failed.
    gui._lkeypad["fg"] = "#00ff00" if keypad._defused else ("#ff0000" if keypad._failed else "#00ffff")
    gui._lwires["fg"] = "#00ff00" if wires._defused else ("#ff0000" if wires._failed else "#00ffff")
    gui._lbutton["fg"] = "#00ff00" if button._defused else ("#ff0000" if button._failed else "#00ffff")
    gui._ltoggles["fg"] = "#00ff00" if toggles._defused else ("#ff0000" if toggles._failed else "#00ffff")
    # check the phases again after a slight delay
    gui.after(100, check_phases)

    # handles a strike
def strike():
    global strikes_left

    # note the strike
    strikes_left -= 1

    # turns off the bomb
def turn_off():
    # stop all threads
    timer._running = False
    keypad._running = False
    wires._running = False
    button._running = False
    toggles._running = False

    # turn off the 7-segment display
    component_7seg.blink_rate = 0
    component_7seg.fill(0)
    # turn off the pushbutton's LED
    for pin in button._rgb:
        pin.value = True


######
# MAIN
######

# initialize the LCD GUI
window = Tk()
gui = Lcd(window)
gui.setupRooms(window)
# initialize the bomb strikes and active phases (i.e., not yet defused)
strikes_left = NUM_STRIKES
active_phases = NUM_PHASES

# "boot" the bomb
gui.after(100, bootup)

# display the LCD GUI
window.mainloop()