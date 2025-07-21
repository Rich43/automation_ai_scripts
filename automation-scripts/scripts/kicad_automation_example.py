import os
import time
import re
from PIL import ImageGrab
import openai
import pyautogui

openai.api_key = os.getenv('OPENAI_API_KEY')
MODEL = 'gpt-4o-mini'
PROMPT_TEMPLATE = (
    "In this KiCad window screenshot, locate the center coordinates of the '{element}' button. Reply as x=###, y=###."
)

# Capture example area (adjust bbox as needed)
img = ImageGrab.grab(bbox=(100, 100, 1400, 900))
img.save('kicad_window.png')

# Request coords
with open('kicad_window.png', 'rb') as f:
    resp = openai.ChatCompletion.create(
        model=MODEL,
        messages=[{'role':'user','content':PROMPT_TEMPLATE.format(element='Place Component')}],
        files=[{'file': f, 'filename': 'kicad_window.png'}]
    )
coords = resp.choices[0].message.content.strip()
match = re.search(r"x=(\d+), y=(\d+)", coords)
if not match:
    raise RuntimeError('Could not parse coordinates')

x, y = map(int, match.groups())

# Click the button
pyautogui.moveTo(x, y, duration=0.2)
pyautogui.click()
print(f"Clicked 'Place Component' at ({x}, {y})")