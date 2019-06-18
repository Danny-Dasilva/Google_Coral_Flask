import time
import io
import threading
import teach


class Camera(object):
    stream = None
    thread = None  # background thread that reads frames from camera
    frame = None  # current frame is stored here by background thread
    last_access = 0  # time of last client access to the camera
    img = None
    def initialize(self):
        if Camera.thread is None:
            # start background frame thread
            Camera.thread = threading.Thread(target=self._thread)
            Camera.thread.start()

            # wait until frames start to be available
            while self.frame is None:
                time.sleep(0)

    def get_frame(self, image):
        global img
        Camera.last_access = time.time()
        img = image
        self.initialize()
        return self.frame

    @classmethod
    def _thread(self):
        global stream
        global img
        while True:
            time.sleep(0.005)
            stream = img
            # store frame
            stream.seek(0)
            self.frame = stream.read()

            # reset stream for next frame
            stream.seek(0)
            stream.truncate()

            # if there hasn't been any clients asking for frames in
            # the last 10 seconds stop the thread
            if time.time() - self.last_access > 10:
                break