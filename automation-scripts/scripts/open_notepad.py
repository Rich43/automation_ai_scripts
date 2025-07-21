import time
import pyautogui

# Coordinates for Start button
START_X, START_Y = 959, 1074

messages = [
    'Hello, this was automated via PyAutoGUI!',
    f'The Start button was clicked at ({START_X}, {START_Y}).',
    'Have a great day!'
]

def open_notepad():
    pyautogui.moveTo(START_X, START_Y, duration=0.2)
    pyautogui.click()
    time.sleep(0.5)
    pyautogui.write('notepad', interval=0.05)
    pyautogui.press('enter')
    time.sleep(1)

if __name__ == '__main__':
    open_notepad()
    for msg in messages:
        pyautogui.write(msg, interval=0.02)
        pyautogui.press('enter')
        time.sleep(0.3)