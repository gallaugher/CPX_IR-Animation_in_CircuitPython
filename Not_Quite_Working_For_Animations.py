import adafruit_irremote
import board
import digitalio
import neopixel
import pulseio

import time
import random
from adafruit_circuitplayground.express import cpx
# Change these to set speed (lower is faster)
FLASH_RATE = 0.250
SPIN_RATE = 0.100
CYLON_RATE = 0.100
BEDAZZLE_RATE = 0.100
CHASE_RATE = 0.100
 
# Change these to be whatever color you want
# Use color picker to come up with hex values
FLASH_COLOR = 0xFF0000
SPIN_COLOR = 0xFF0000
CYLON_COLOR = 0xFF0000
 
# Define 10 colors here.
# Must be 10 entries.
# Use 0x000000 if you want a blank space.
RAINBOW_COLORS = (
  0xFF0000,   
  0xFF5500,
  0xFFFF00,
  0x00FF00,
  0x0000FF,
  0xFF00FF,
  0x000000,
  0x000000,
  0x000000,
  0x000000
)


#pixels = neopixel.NeoPixel(cpx.NEOPIXEL, 10)

red_led = cpx.red_led
# red_led.direction = digitalio.Direction.OUTPUT

# pulsein = pulseio.PulseIn(board.REMOTEIN, maxlen=120, idle_state=True)
pulsein = pulseio.PulseIn(board.IR_RX, maxlen=120, idle_state=True)
decoder = adafruit_irremote.GenericDecode()

pulsein.clear()
pulsein.resume()

# Expected pulse, pasted in from previous recording REPL session:
pulse = [207, 231, 133, 239, 199, 165, 189, 181, 173, 151, 111]

# among others, this example works with the Adafruit mini IR remote:
# https://www.adafruit.com/product/389
# size must match what you are decoding! for NEC use 4
received_code = bytearray(4)

# IR Remote Mapping
'''
 1: [255, 2, 247, 8]
 2: [255, 2, 119, 136]
 3: [255, 2, 183, 72]
 4: [255, 2, 215, 40]
 5: [255, 2, 87, 168]
 6: [255, 2, 151, 104]
 7: [255, 2, 231, 24]
 8: [255, 2, 103, 152]
 9: [255, 2, 167, 88]
 0: [255, 2, 207, 48]

^ : [255, 2, 95, 160]
v : [255, 2, 79, 176]
> : [255, 2, 175, 80]
< : [255, 2, 239, 16]

Enter: [255, 2, 111, 144]
Setup: [255, 2, 223, 32]
Stop/Mode: [255, 2, 159, 96]
Back: [255, 2, 143, 112]

Vol - : [255, 2, 255, 0]
Vol + : [255, 2, 191, 64]

Play/Pause: [255, 2, 127, 128]

----
ABOVE IS NEC REMOTE
BELOW IS JOHN'S REMOTE

 1: [255, 0, 207, 48]  command: 207
 2: [255, 0, 231, 24]  command: 231
 3: [255, 0, 133, 122] command: 133
 4: [255, 0, 239, 16] command: 239
 5: [255, 0, 199, 56] command: 199
 6: [255, 0, 165, 90] command: 165
 7: [255, 2, 231, 24] command: 189
 8: [255, 0, 181, 74] command: 181
 9: [255, 0, 173, 82] command: 173
 0: [255, 0, 151, 104] command 151

^ : [255, 0, 111, 144] command 111
v : [255, 2, 79, 176]
> : [255, 2, 175, 80]
< : [255, 2, 239, 16]
'''

RED = (255, 0, 0)
GREEN = (0, 255, 0)
WHITE = (85, 85, 85)
BLUE = (0, 0, 255)
PINK = (128, 0, 128)
YELLOW = (148, 108, 0)
PURPLE = (200, 0, 55)
TEAL = (0, 200, 100)
ORANGE = (100, 45, 0)
BLACK = (0, 0, 0)

last_command = None

# Below is code taken from Adafruit's CPX CircuitPython Bike Signal at:
# https://learn.adafruit.com/circuit-playground-bike-light/the-all-of-them-circuitpython
# Thanks for the code, Carter Nelson!
# https://learn.adafruit.com/users/caternuson

def fuzzy_pulse_compare(pulse1, pulse2, fuzzyness=0.2):
    if len(pulse1) != len(pulse2):
        return False
    for i in range(len(pulse1)):
        threshold = int(pulse1[i] * fuzzyness)
        if abs(pulse1[i] - pulse2[i]) > threshold:
            return False
    return True
 
def rainbow():
    # Start at the beginning
    start_color = 0
 
    # original while from Bike Light commented out
    # while not buttons_pressed():
    # using a while True: and intend to break it when a pulse is received
    while True:
        # Turn off all the NeoPixels
        cpx.pixels.fill(0)
 
        # Loop through and set pixels
        color = start_color
        for p in range(10):
            cpx.pixels[p] = RAINBOW_COLORS[color]
            color += 1
            color = color if color < 10 else 0
            
        # Increment start index into color array
        start_color += 1
        
        # Check value and reset if necessary
        start_color = start_color if start_color < 10 else 0
        
        # Wait a little bit so we don't spin too fast
        time.sleep(CHASE_RATE)
        print("LOOPING IN RAINBOW")
        detected = decoder.read_pulses(pulsein)
        print("*** detected = ", detected)
        if fuzzy_pulse_compare(pulse, detected):
            print("!!!! fuzzy pulse compare is TRUE !!! ")
            break
    
while True:
    red_led= False
    try:
        pulses = decoder.read_pulses(pulsein)
    except MemoryError as e:
        print("Memory error: ", e)
        continue
    red_led= True
    print("Heard", len(pulses), "Pulses:", pulses)
    command = None
    try:
        code = decoder.decode_bits(pulses, debug=False)
        if len(code) > 3:
            command = code[2]
        print("Decoded:", code)
    except adafruit_irremote.IRNECRepeatException:  # unusual short code!
        print("NEC repeat!")
        command = last_command
    except adafruit_irremote.IRDecodeException as e:  # failed to decode
        print("Failed to decode:", e)
    except MemoryError as e:
        print("Memory error: ", e)

    if not command:
        continue
    last_command = command

    print("----------------------------")
    red_led = False

    if command == 207:  # IR button 1
        cpx.pixels.fill(RED)
    elif command == 231:  # 2
        cpx.pixels.fill(GREEN)
    elif command == 133:  # 3
        cpx.pixels.fill(WHITE)
    elif command == 239:  # 4
        cpx.pixels.fill(BLUE)
    elif command == 199:  # 5
        cpx.pixels.fill(PINK)
    elif command == 165:  # 6
        cpx.pixels.fill(YELLOW)
    elif command == 189:  # 7
        cpx.pixels.fill(PURPLE)
    elif command == 181:  # 8
        cpx.pixels.fill(TEAL)
    elif command == 173:  # 9
        cpx.pixels.fill(ORANGE)
    elif command == 151:
        cpx.pixels.fill(BLACK)  # 0/10+
    elif command == 111:
        rainbow()   ; time.sleep(0.25)