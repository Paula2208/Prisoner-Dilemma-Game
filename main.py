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
BTN_A = 19
BTN_B = 26

class GameState:
    def _init_(self):
        self.pts_A = 0
        self.pts_B = 0
        self.multi_rounds = False
        self.num_rounds = 0
        self.current_round = 0
        self.last_player_A_move = None
        self.game_mode_selected = False
        self.game_started = False

def init_gpio():
    """Initialize GPIO with proper cleanup first"""
    GPIO.cleanup()
    GPIO.setmode(GPIO.BCM)
    
    # Setup LED pins as outputs
    led_pins = [LED_A_RED, LED_A_GREEN, LED_A_BLUE, 
                LED_B_RED, LED_B_GREEN, LED_B_BLUE]
    for pin in led_pins:
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, GPIO.HIGH)  # Set to HIGH initially (turn LEDs off)
    
    # Setup button pins as inputs with pull-up
    GPIO.setup(BTN_A, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(BTN_B, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    print("GPIO initialized successfully")

def set_color(led_pins, color):
    """Turns an RGB LED on with the specified color."""
    try:
        red, green, blue = color
        GPIO.output(led_pins[0], GPIO.LOW if red == 1 else GPIO.HIGH)    # LED rojo
        GPIO.output(led_pins[1], GPIO.LOW if green == 1 else GPIO.HIGH)  # LED verde
        GPIO.output(led_pins[2], GPIO.LOW if blue == 1 else GPIO.HIGH)   # LED azul
    except Exception as e:
        print(f"Error setting LED color: {e}")


def update_display(oled, font, text_lines):
    """Updates both OLED screen and console with given text lines."""
    try:
        # Update OLED
        image = Image.new("1", (oled.width, oled.height))
        draw = ImageDraw.Draw(image)
        
        y_position = 10
        for line in text_lines:
            draw.text((10, y_position), line, font=font, fill=255)
            y_position += 20
            
        oled.image(image)
        oled.show()

        # Print to console with formatting
        print("\n" + "="*50)
        for line in text_lines:
            print(line)
        print("="*50 + "\n")

    except Exception as e:
        print(f"Error updating display: {e}")

def play_robot(game_state):
    """Robot's move logic"""
    if not game_state.multi_rounds:
        return "r", (1, 0, 0)  # Red (betray)

    if game_state.current_round == 1:
        return "g", (0, 1, 0)  # Green (cooperate)

    if game_state.last_player_A_move == "g":
        return "g", (0, 1, 0)  # Green (cooperate)
    else:
        if random.random() < 0.9:  # 90% chance to betray
            return "r", (1, 0, 0)  # Red (betray)
        else:
            return "g", (0, 1, 0)  # Green (cooperate)

def handle_game_round(game_state, player_move, oled, font):
    """Handle a single round of the game"""
    print(f"\nRound {game_state.current_round + 1} starting...")
    
    # Print player's move
    move_text = "cooperate" if player_move == "g" else "betray"
    print(f"Player chose to {move_text}")
    
    # Player A's move
    if player_move == "g":
        set_color((LED_A_RED, LED_A_GREEN, LED_A_BLUE), (0, 1, 0))  # Green
    else:
        set_color((LED_A_RED, LED_A_GREEN, LED_A_BLUE), (1, 0, 0))  # Red

    # Robot's move
    robot_move, robot_color = play_robot(game_state)
    set_color((LED_B_RED, LED_B_GREEN, LED_B_BLUE), robot_color)

    sleep(2)
    
    # Turn off LEDs
    set_color((LED_A_RED, LED_A_GREEN, LED_A_BLUE), (0, 0, 0))
    set_color((LED_B_RED, LED_B_GREEN, LED_B_BLUE), (0, 0, 0))
    
    # Calculate scores
    if player_move == "g" and robot_move == "g":
        set_color((LED_B_RED, LED_B_GREEN, LED_B_BLUE), (0, 1, 0))  # Green
        game_state.pts_A += 3
        game_state.pts_B += 3
        result = "Both cooperated!"

    elif player_move == "r" and robot_move == "r":
        set_color((LED_B_RED, LED_B_GREEN, LED_B_BLUE), (1, 0, 0))  # Red
        game_state.pts_A += 1
        game_state.pts_B += 1
        result = "Both betrayed!"

    elif player_move == "r" and robot_move == "g":
        set_color((LED_B_RED, LED_B_GREEN, LED_B_BLUE), (0, 1, 1))  # Cyan
        game_state.pts_A += 5
        result = "You took advantage!"

    else:
        set_color((LED_B_RED, LED_B_GREEN, LED_B_BLUE), (1, 1, 0))  # Yellow
        game_state.pts_B += 5
        result = "Robot took advantage!"

    print(f"\nRound result: {result}")
    print(f"Current scores - Player: {game_state.pts_A}, Robot: {game_state.pts_B}")

    # Update display
    update_display(oled, font, [
        f"Player A: {game_state.pts_A}",
        f"Player B: {game_state.pts_B}",
        result
    ])
    
    game_state.last_player_A_move = player_move
    game_state.current_round += 1

    sleep(5) # Waiting time between rounds

def main():
    # Initialize GPIO
    print("\nInitializing game system...")
    init_gpio()
    
    # Initialize I2C and OLED
    try:
        i2c = busio.I2C(board.SCL, board.SDA)
        oled = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c)
        oled.fill(0)
        oled.show()
        font = ImageFont.load_default()
        print("OLED display initialized successfully")
    except Exception as e:
        print(f"Error initializing OLED: {e}")
        GPIO.cleanup()
        return

    # Initialize game state
    game_state = GameState()
    
    # Welcome message
    print("\n" + "="*60)
    print("Welcome to Prisoner's Dilemma Game!")
    print("="*60 + "\n")
    
    update_display(oled, font, [
        "Welcome to",
        "Prisoner's Dilemma",
        "Game!"
    ])
    sleep(4)
    
    # Game loop
    try:
        while True:
            if not game_state.game_mode_selected:
                # Mode selection phase
                print("\nWaiting for game mode selection...")
                print("Press G (Button A) for single round")
                print("Press R (Button B) for multiple rounds")
                
                update_display(oled, font, [
                    "Select mode:",
                    "G: One round",
                    "R: Multiple rounds"
                ])
                
                # Check buttons for mode selection
                if not GPIO.input(BTN_A):  # Button A pressed
                    game_state.multi_rounds = False
                    game_state.game_mode_selected = True
                    print("\nSingle round mode selected!")
                    sleep(1)  # Debounce
                elif not GPIO.input(BTN_B):  # Button B pressed
                    game_state.multi_rounds = True
                    game_state.num_rounds = random.randint(3, 15)
                    game_state.game_mode_selected = True
                    print(f"\nMultiple round mode selected - {game_state.num_rounds} rounds!")
                    sleep(1)  # Debounce
            
            else:
                # Game phase
                update_display(oled, font, [
                    "Press G to Cooperate",
                    "Press R to Betray",
                    f"Round: {game_state.current_round + 1}"
                ])
                
                # Check buttons for game moves
                if not GPIO.input(BTN_A):  # Cooperate
                    handle_game_round(game_state, "g", oled, font)
                    sleep(1)
                elif not GPIO.input(BTN_B):  # Betray
                    handle_game_round(game_state, "r", oled, font)
                    sleep(1)
                
                # Check if game should end
                if game_state.multi_rounds and game_state.current_round >= game_state.num_rounds:
                    print("\nGame Over!")
                    # Show final results
                    if game_state.pts_A > game_state.pts_B:
                        result = "You Win!"
                    elif game_state.pts_B > game_state.pts_A:
                        result = "Robot Wins!"
                    else:
                        result = "It's a Tie!"
                    
                    print(f"\nFinal Result: {result}")
                    print(f"Final Score - Player: {game_state.pts_A}, Robot: {game_state.pts_B}")
                        
                    update_display(oled, font, [
                        result,
                        f"Final Score: {game_state.pts_A}-{game_state.pts_B}",
                        "Press any button to restart"
                    ])
                    
                    print("\nPress any button to start a new game...")
                    # Wait for button press to restart
                    while GPIO.input(BTN_A) and GPIO.input(BTN_B):
                        sleep(0.6)
                    
                    # Reset game state
                    game_state = GameState()
                    print("\nStarting new game...")
                    sleep(1)
            
            sleep(0.6)  # Prevent CPU overload
            
    except KeyboardInterrupt:
        print("\nGame interrupted by user. Exiting...")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        GPIO.cleanup()
        print("\nGPIO cleanup complete. Thanks for playing! Goodbye!")

if __name__ == "_main_":
    main()