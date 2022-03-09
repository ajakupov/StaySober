import cv2
import os
import pafy
import numpy as np


class TrainSetGenerator:
    # BGR color constants
    WHITE = (255, 255, 255)
    BLUE = (255, 0, 0)
    GREEN = (0, 255, 0)
    RED = (0, 0, 255)
    BLACK = (0, 0, 0)

    def __init__(self, video_url):
        prototxt = "./ml_artifacts/deploy.prototxt.txt"
        model = "./ml_artifacts/res10_300x300_ssd_iter_140000.caffemodel"

        self.min_confidence = 0.5
        video = pafy.new(video_url)
        self.cached_video = video.getbest(preftype="mp4")
        self.net = cv2.dnn.readNetFromCaffe(prototxt, model)

    def capture_faces(self):
        video_capture = cv2.VideoCapture(self.cached_video.url)
        frame_counter = 0

        while video_capture.isOpened():
            _, frame = video_capture.read()
            frame_counter += 1
            (h, w) = frame.shape[:2]
            blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)), 1.0, (300, 300), (104.0, 177.0, 123.0))
            self.net.setInput(blob)
            detections = self.net.forward()

            for i in range(0, detections.shape[2]):
                confidence = detections[0, 0, i, 2]

                if confidence < self.min_confidence:
                    continue

                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                (startX, startY, endX, endY) = box.astype("int")
                face_frame = frame[startY:endY, startX:endX]
                if abs(startX-210) < 100:
                    frame_color = self.GREEN
                    if frame_counter % 100 == 0:
                        save_image(face_frame, "faces/sober")
                elif abs(startX-575) < 100:
                    frame_color = self.RED
                    if frame_counter % 100 == 0:
                        save_image(face_frame, "faces/alcoholic")
                else:
                    frame_color = self.BLUE

                cv2.rectangle(frame, (startX, startY), (endX, endY), frame_color, 2)

                cv2.imshow("Frame", frame)
                key = cv2.waitKey(1) & 0xFF

                if key == ord("q"):
                    break
        video_capture.release()
        cv2.destroyAllWindows()


def save_image(image, folder):
    """Save an image with unique name
    Arguments:
        image {OpanCV} -- image object to be saved
        folder {string} -- output folder
    """

    # check whether the folder exists and create one if not
    if not os.path.exists(folder):
        os.makedirs(folder)

    # to not erase previously saved photos counter (image name) = number of photos in a folder + 1
    image_counter = len([name for name in os.listdir(folder)
                         if os.path.isfile(os.path.join(folder, name))])

    # increment image counter
    image_counter += 1

    # save image to the dedicated folder (folder name = label)
    cv2.imwrite(folder + '/' + str(image_counter) + '.png', image)