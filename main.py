import RPi.GPIO as GPIO
import random
import board
import busio
import adafruit_ssd1306
from PIL import Image, ImageDraw, ImageFont
from time import sleep

# Define RGB LED pins
LED_A_RED = 17
LED_A_GREEN = 27
LED_A_BLUE = 22

LED_B_RED = 18
LED_B_GREEN = 23
LED_B_BLUE = 24

# Define Button pins
BTN_A = 5
BTN_B = 6

# Initialize GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup([LED_A_RED, LED_A_GREEN, LED_A_BLUE, LED_B_RED, LED_B_GREEN, LED_B_BLUE], GPIO.OUT)
GPIO.setup([BTN_A, BTN_B], GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Initialize I2C for OLED Display
i2c = busio.I2C(board.SCL, board.SDA)
oled = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c)

# Clear OLED display
oled.fill(0)
oled.show()

# Load a font
font = ImageFont.load_default()

# Player scores
pts_A = 0
pts_B = 0

def set_color(led_pins, color):
    """Turns an RGB LED on with the specified color."""
    GPIO.output(led_pins, (color[0], color[1], color[2]))

def update_display():
    """Updates the OLED screen with the current scores."""
    image = Image.new("1", (oled.width, oled.height))
    draw = ImageDraw.Draw(image)

    draw.text((10, 10), f"Player A: {pts_A}", font=font, fill=255)
    draw.text((10, 30), f"Player B: {pts_B}", font=font, fill=255)

    oled.image(image)
    oled.show()

def play(color_A):
    """Handles the game logic when a button is pressed."""
    global pts_A, pts_B

    # Set LED A color
    if color_A == "g":
        set_color((LED_A_RED, LED_A_GREEN, LED_A_BLUE), (0, 1, 0))  # Green
    else:
        color_A = "r"
        set_color((LED_A_RED, LED_A_GREEN, LED_A_BLUE), (1, 0, 0))  # Red

    # Choose a random color for LED B
    color_B = random.choice(["g", "r"])
    set_color((LED_B_RED, LED_B_GREEN, LED_B_BLUE), (0, 1, 0) if color_B == "g" else (1, 0, 0))

    sleep(2)

    # Turn off both LEDs
    set_color((LED_A_RED, LED_A_GREEN, LED_A_BLUE), (0, 0, 0))
    set_color((LED_B_RED, LED_B_GREEN, LED_B_BLUE), (0, 0, 0))

    sleep(0.2)

    # Determine the outcome and update scores
    if color_A == "g" and color_B == "g":
        set_color((LED_B_RED, LED_B_GREEN, LED_B_BLUE), (0, 1, 0))  # Green
        print("Both players cooperated")
        pts_A += 3
        pts_B += 3

    elif color_A == "r" and color_B == "r":
        set_color((LED_B_RED, LED_B_GREEN, LED_B_BLUE), (1, 0, 0))  # Red
        print("No cooperation")
        pts_A += 1
        pts_B += 1

    elif color_A == "r" and color_B == "g":
        set_color((LED_B_RED, LED_B_GREEN, LED_B_BLUE), (0, 1, 1))  # Cyan
        print("Player A has an advantage")
        pts_A += 5

    elif color_A == "g" and color_B == "r":
        set_color((LED_B_RED, LED_B_GREEN, LED_B_BLUE), (1, 1, 0))  # Yellow
        print("Player B has an advantage")
        pts_B += 5

    sleep(1)
    set_color((LED_B_RED, LED_B_GREEN, LED_B_BLUE), (0, 0, 0))

    # Print the current scores
    print(f"Score: Player A - {pts_A}, Player B - {pts_B}")

    # Update scores on OLED display
    update_display()

# Set up button event handlers
GPIO.add_event_detect(BTN_A, GPIO.FALLING, callback=lambda x: play("g"), bouncetime=300)
GPIO.add_event_detect(BTN_B, GPIO.FALLING, callback=lambda x: play("r"), bouncetime=300)

print("Hi! Welcome to Prisoner's Dilemma Game")
print("\n\nSelect game mode: ")
print("One round (press button G)") # btn_A
print("Multiple rounds (press button R)") #btn_B

# @todo

try:
    while True:
        sleep(0.01)

except KeyboardInterrupt:
    print("Exiting...")
    GPIO.cleanup()
    print("Bye! See you later :)")