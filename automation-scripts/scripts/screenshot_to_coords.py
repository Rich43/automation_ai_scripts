import os
import openai
from PIL import ImageGrab

# Configuration
openai.api_key = os.getenv('OPENAI_API_KEY')
MODEL = 'gpt-4o-mini'
PROMPT = 'In this screenshot, locate the center coordinates of the Windows Start button. Reply as x=###, y=###.'

# Capture and save screenshot
test_img = ImageGrab.grab()
test_img.save('desktop.png')

# Send to OpenAI
with open('desktop.png', 'rb') as f:
    resp = openai.ChatCompletion.create(
        model=MODEL,
        messages=[{'role':'user','content':PROMPT}],
        files=[{'file': f, 'filename': 'desktop.png'}]
    )
print(resp.choices[0].message.content)