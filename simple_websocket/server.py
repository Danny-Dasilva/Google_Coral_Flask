from Cam import camera
from flask import Flask, send_file, Response, render_template

Image = camera()
app = Flask(__name__)
@app.route('/video_feed')
def video_feed():
    return Response(Image.ImageStream(), mimetype='multipart/x-mixed-replace; boundary=frame')
@app.route('/')
def index():
    return 'functional'

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=False)
