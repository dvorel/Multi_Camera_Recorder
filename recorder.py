import threading
import os
import cv2
from time import sleep

class Camera:
    def __init__(self, id=0, resolution=(1920, 1080)):
        self.id = id
        self.cap = self._cap_start(resolution)
        self._video = False
        self._videoWriter = None

    def _cap_start(self, res):
        cap = cv2.VideoCapture(self.id)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, res[0])
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, res[1])      

        return cap

    def _get_file(self, path):
        if os.path.exists(path):
            i = 0
            while True:
                nextPath = os.path.join(path, "recording_" + str(i) + ".avi")
                if not os.path.exists(nextPath):
                    return nextPath
                i+=1
        else:
            os.makedirs(path)

        return os.path.join(path, "recording_0.avi")


    def start_video(self, path, resolution=(1920, 1080)):
        file = self._get_file(path)
        self._video = True
        
        self._videoWriter = cv2.VideoWriter(file, cv2.VideoWriter_fourcc(*"DIVX"), 30, resolution)


    def save(self, dst=None, extension="jpg"):
        read, img = self.cap.read() 
        if read:
            if self._video:
                self._videoWriter.write(img)
            else:
                dst+="." + extension
                cv2.imwrite(dst, img)
        
        return read


class Recorder:
    def __init__(self, path):
        self.path = self._get_path(path)

        self.streams = list()
        self.threads = list()
        self.running = False
    
    def _get_path(self, dir):
        if os.path.exists(dir):
            i = 0
            while True:
                nextPath = os.path.join(dir, "run" + str(i))
                if not os.path.exists(nextPath):
                    return nextPath
                i+=1

        return os.path.join(dir, "run0")

    def record(self, camera, dst, lock, delay=33):
        if camera._video == False:
            os.makedirs(dst, exist_ok=True)

        i=0

        while self.running:
            lock.acquire()
            
            saved = camera.save(os.path.join(dst, str(i)))

            if not saved:
                raise Exception(f"Camera {camera.id} failed to read frame.")

            i+=1
            cv2.waitKey(delay)

            lock.release()

    def start(self):
        lock = threading.Lock()
        self.running = True

        for i, cam in enumerate(self.streams):
            self.threads.append(threading.Thread(target=self.record, args=(cam, os.path.join(self.path, str(i)), lock)))
        
        for t in self.threads:
            t.start()
    
    def stop(self):
        self.running = False

        for t in self.threads:
            t.join()
        

if __name__ == "__main__":
    rec = Recorder("Test_record")
    rec.streams.append(Camera(0))
    rec.streams[0].start_video("Test_video")
    #rec.streams.append(Camera(0))

    rec.start()

    sleep(5)

    rec.stop()