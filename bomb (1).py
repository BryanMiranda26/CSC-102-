#################################
# CSC 102 Defuse the Bomb Project
# Main program
# Team: Gabriel Chiaravalloti, Bryan Miranda-Cruz, Christian Badenhausen
#################################

# import the configs
from bomb_configs import *
# import the phases
from bomb_phases import *
from random import randint, choice
import time, random

# ------------- Color Ninja mini game state -------------
def color_ninja_button_press():
    """Called when the physical bomb button is pressed."""
    global score, lives, waiting_for_press, current_target

    if not waiting_for_press:
        return

    # Slice attempt
    if current_target == "fruit":
        score += 1
    else:
        lives -= 1

    gui._lscore_game.config(text=f"Score: {score}     Lives: {lives}")

    waiting_for_press = False
    clear_target()
    
current_target = None          # "fruit" or "bomb"
current_color = None           # actual color name
target_expires_at = 0
score = 0
lives = 3
waiting_for_press = False
last_button_down = False


def spawn_target():
    global current_target, current_color, target_expires_at, waiting_for_press

    # 75 percent fruit, 25 percent bomb
    if random.random() < 0.75:
        current_target = "fruit"
        current_color = random.choice(["green", "yellow", "blue"])
    else:
        current_target = "bomb"
        current_color = "red"

    waiting_for_press = True
    target_expires_at = time.time() + 1.0   # visible for 1 second

    # update the label on the LCD
    if current_target == "bomb":
        gui._lcolor_game.config(text="BOMB", bg=current_color, fg="white")
    else:
        gui._lcolor_game.config(text="FRUIT", bg=current_color, fg="black")


def clear_target():
    global current_target
    current_target = None
    gui._lcolor_game.config(text="Color game:", bg="black", fg="#00ff00")


def game_loop():
    global current_target, waiting_for_press, lives, target_expires_at, last_button_down, score

    now = time.time()

    # spawn a new target if we do not have one
    if current_target is None:
        spawn_target()

    # read the real bomb button as input
    button_down_now = False
    try:
        # button is created in setup_phases when RPi is True
        button_down_now = bool(button._value)
    except NameError:
        # button not created yet
        button_down_now = False
    except:
        button_down_now = False

    # rising edge: not down last frame, down this frame
    if button_down_now and not last_button_down and waiting_for_press:
        if current_target == "fruit":
            score += 1
        else:
            lives -= 1

        gui._lscore_game.config(text=f"Score: {score}     Lives: {lives}")
        waiting_for_press = False
        clear_target()

    # remember state for next tick
    last_button_down = button_down_now

    # target expired without press
    if current_target is not None and now > target_expires_at:
        waiting_for_press = False
        clear_target()

    # game over
    if lives <= 0:
        gui._lcolor_game.config(text="GAME OVER", bg="black", fg="red")
        return  # stop the game loop but bomb still runs

    # schedule next tick
    gui.after(50, game_loop)  # 20 updates per second

###########
# functions
###########
# generates the bootup sequence on the LCD
def bootup(n=0):
    gui._lscroll["text"] = boot_text.replace("\x00", "")
    # configure the remaining GUI widgets
    gui.setup()
    gui._lkeypad.grid_remove()
    gui._lwires.grid_remove()
    gui._lbutton.grid_remove()
    gui._ltoggles.grid_remove()
    
    gui._lkeypad.grid()

    # ---------- Color Ninja labels on the LCD ----------
    # place them near the bottom of the grid
    gui._lcolor_game = Label(gui, bg="black", fg="#00ff00",
                             font=("Courier New", 18), text="Color game:")
    gui._lcolor_game.grid(row=7, column=0, columnspan=3, sticky=W)

    gui._lscore_game = Label(gui, bg="black", fg="#00ff00",
                             font=("Courier New", 18), text="Score: 0     Lives: 3")
    gui._lscore_game.grid(row=8, column=0, columnspan=3, sticky=W)

    # start the mini game loop a moment after boot
    gui.after(200, game_loop)
    # ---------------------------------------------------

    # setup the phase threads, execute them, and check their statuses
    if (RPi):
        setup_phases()
        check_phases()
   
# sets up the phase threads
def setup_phases():
    global timer, keypad, wires, button, toggles
    
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
    # setup the toggle switches thread
    toggles = Toggles(component_toggles, toggles_target)

    # start the phase threads
    timer.start()
    keypad.start()
    wires.start()
    button.start()
    toggles.start()

# checks the phase threads
def check_phases():
    global active_phases
    
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
    # check the keypad
    if (keypad._running):
        # update the GUI
        if not keypad._defused:
            gui._lkeypad["text"] = (
                f"{riddle_text}\n"
                f"Input: {keypad._value}"
        )
    else:
        gui._lkeypad["text"] = "Keypad: DEFUSED"

        # the phase is defused -> stop the thread
        if (keypad._defused):
            keypad._running = False
            active_phases -= 1

    # HIDE KEYPAD, SHOW TOGGLES
            gui._lkeypad.grid_remove()
            gui._ltoggles.grid()

        # the phase has failed -> strike
        elif (keypad._failed):
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
            strike()
            # reset the button
            button._failed = False
    # check the toggles
    if (toggles._running):
        # update the GUI
        if not toggles._defused:
            gui._ltoggles["text"] = (
                f"{toggles_riddle_text}\n"
                f"Bits: {getattr(toggles,'_bits','----')}  =  {getattr(toggles,'_value','')}"
            )
        else:
            gui._ltoggles["text"] = "Toggles: DEFUSED"
        # the phase is defused -> stop the thread
        if (toggles._defused):
            toggles._running = False
            active_phases -= 1
        # the phase has failed -> strike
        elif (toggles._failed):
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

# initialize the bomb strikes and active phases (i.e., not yet defused)
strikes_left = NUM_STRIKES
active_phases = NUM_PHASES

# "boot" the bomb
gui.after(100, bootup)

# display the LCD GUI
window.mainloop()

