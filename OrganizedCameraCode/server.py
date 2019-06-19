from flask import Flask, send_file, Response, render_template
from Cam import camera
import time
Image = camera()
time.sleep(2)

def main():
    img = Image.PILImage()
    # print(img)
    time.sleep(0.1)

if __name__ == "__main__":
    while True:
        try:
            main()
        except KeyboardInterrupt:
            break
