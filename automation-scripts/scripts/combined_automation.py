import os
import time
import re
from PIL import ImageGrab
import openai
import pyautogui

# Config
openai.api_key = os.getenv('OPENAI_API_KEY')
MODEL = 'gpt-4o-mini'
PROMPT = 'In this desktop screenshot, find the pixel coordinates of the center of the Windows Start button. Return as x=###, y=###'

# 1. Screenshot
test_img = ImageGrab.grab()
test_img.save('desktop.png')

# 2. Vision API response
with open('desktop.png', 'rb') as f:
    resp = openai.ChatCompletion.create(
        model=MODEL,
        messages=[{'role':'user','content':PROMPT}],
        files=[{'file': f, 'filename': 'desktop.png'}]
    )
reply = resp.choices[0].message.content.strip()

# 3. Parse coords using regex
m = re.search(r"x=(\d+), y=(\d+)", reply)
if not m:
    raise ValueError('Could not parse coordinates')
x, y = map(int, m.groups())

# 4. Automate
pyautogui.moveTo(x, y, duration=0.2)
pyautogui.click()