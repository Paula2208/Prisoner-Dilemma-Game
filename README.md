# Prisoner's Dilemma Game

This project is a **game for one players** using **RGB LEDs, buttons, and an OLED display** on a **Raspberry Pi**.  
Player press buttons to make a decision, and their choices affect their scores based on **cooperation or competition** according with Prisoner's Dilemma Game.

## 👋🏼 How to play
* [Run the Game](#🚀-running-the-game)
* Select your game mode (one or multi round)
* Make a decision: Press G button for Cooperation or press R button for NO-coop
* 🤖 A robot will make a decision too (see on their led)

After decision taken:
* 🟢 **Led Green:**     Both cooperated and each earns 3 points ✅
* 🔴 **Led Red:**       Both NO-cooperated and each earns 1 points ❌
* 🩵 **Led Cyan:**      You take advantage and earn 5 points (robot 0pts) 👩🏻‍💻
* 🟡 **Led Yellow:**    Robot takes advantage and earns 5 points (you 0 pts) 🤖

You can see remaining points on OLED display. **The one with the most points wins**.

Enjoy!!

## 📦 Installation

### 🛠️ Requirements
- **Raspberry Pi** (any model with GPIO support)
- **RGB LEDs** (2x, connected to GPIO)
- **Push buttons** (2x, connected to GPIO)
- **SSD1306 OLED Display** (I2C)
- **Resistors** for pull-down setup and leds

### 1️⃣ Clone the Repository
```bash
    git clone https://github.com/Paula2208/Prisoner-Dilemma-Game.git
    cd Prisoner-Dilemma-Game
```

### 2️⃣ Install Dependencies
```bash
    pip install -r requirements.txt
```

### 3️⃣ Enable I2C on Raspberry Pi
```bash
    sudo raspi-config
```
* Go to Interfacing Options > I2C > Enable
* Restart the Raspberry Pi.

## 🚀 Running the Game
```bash
    python main.py
```

## 🔧 GPIO Pin Configuration

| Component | Player A | Player B (🤖) |
|-----------|----------|---------------|
| Red LED   | GPIO 17  | GPIO 18       |
| Green LED | GPIO 27  | GPIO 23       |
| Blue LED  | GPIO 22  | GPIO 24       |
| Button    | GPIO 5   | GPIO 6        |

## 🔄 Stopping the Game

Press Ctrl+C to stop the game safely.
All GPIO pins will be cleaned up automatically.