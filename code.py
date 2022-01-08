import time
import digitalio
import board
import usb_hid
from adafruit_debouncer import Debouncer
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode


# ======================
# Application Settings
# --------------------
startsZoomAudioOn = True
startsZoomVideoOn = True

btnThreshold = 20
quitBtnThreshold = 12


# ========================
# Application State Vars
# ----------------------
greenBtnPressedFor = 0
blueBtnPressedFor = 0
quitBtnPressedFor = 0
inZoom = False


# ====================
# Green Button Setup
# ------------------
greenBtnIO = digitalio.DigitalInOut(board.GP18)
greenBtnIO.direction = digitalio.Direction.INPUT
greenBtnIO.pull = digitalio.Pull.UP

greenBtn = Debouncer(greenBtnIO)

greenBtnLight = digitalio.DigitalInOut(board.GP21)
greenBtnLight.direction = digitalio.Direction.OUTPUT


# ===================
# Blue Button Setup
# -----------------
blueBtnIO = digitalio.DigitalInOut(board.GP13)
blueBtnIO.direction = digitalio.Direction.INPUT
blueBtnIO.pull = digitalio.Pull.UP

blueBtn = Debouncer(blueBtnIO)

blueBtnLight = digitalio.DigitalInOut(board.GP10)
blueBtnLight.direction = digitalio.Direction.OUTPUT


# ===================
# Quit Button Setup
# -----------------
quitBtnIO = digitalio.DigitalInOut(board.GP22)
quitBtnIO.direction = digitalio.Direction.INPUT
quitBtnIO.pull = digitalio.Pull.UP
quitBtn = Debouncer(quitBtnIO)


# ====================
# Status Light Setup
# ------------------
statusLight = digitalio.DigitalInOut(board.GP2)
statusLight.direction = digitalio.Direction.OUTPUT


# ========================
# Virtual keyboard setup
# ----------------------
keyboard = Keyboard(usb_hid.devices)


# ==========
# Run Loop
# --------
while True:
    quitBtn.update()
    
    # Event that turns on zoom controls
    if quitBtn.fell:
        inZoom = True
        statusLight.value = True
        greenBtnLight.value = startsZoomAudioOn
        blueBtnLight.value = startsZoomVideoOn

    # Event that turns off zoom controls and quits meeting after
    # a long hold
    elif not quitBtn.value:
        quitBtnPressedFor = quitBtnPressedFor + 1
        
        if quitBtnPressedFor > quitBtnThreshold:
            inZoom = False
            quitBtnPressedFor = 0
            statusLight.value = False
            greenBtnLight.value = False
            blueBtnLight.value = False
            keyboard.send(Keycode.GUI, Keycode.W)

    if inZoom:
        # Only continues on if the Zoom setting is on
        greenBtn.update()
        blueBtn.update()
        

        # Event that happens once on green button press
        if greenBtn.fell:
            greenBtnLight.value = not greenBtnLight.value
            keyboard.send(Keycode.GUI, Keycode.SHIFT, Keycode.A)

        # Resets timing when the green button is lifted
        elif greenBtn.rose:
            greenBtnPressedFor = 0
    
        # Fires when button is held; increases timer as held, to flip button light state
        elif not greenBtn.value:
            greenBtnPressedFor = greenBtnPressedFor + 1
            
            if greenBtnPressedFor > btnThreshold:
                greenBtnLight.value = not greenBtnLight.value
                greenBtnPressedFor = 0


        if blueBtn.fell:
            blueBtnLight.value = not blueBtnLight.value
            keyboard.send(Keycode.GUI, Keycode.SHIFT, Keycode.V)

        elif blueBtn.rose:
            blueBtnPressedFor = 0
        
        elif not blueBtn.value:
            blueBtnPressedFor = blueBtnPressedFor + 1
            
            if blueBtnPressedFor > btnThreshold:
                blueBtnLight.value = not blueBtnLight.value
                blueBtnPressedFor = 0


    # pause before looping
    time.sleep(0.1)
