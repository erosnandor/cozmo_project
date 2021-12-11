import numpy as np
import torch
import torchvision
import torchvision.transforms as T
import cv2
import threading
from PIL import Image
import io

STOP = False
FRAME = 'empty' # easier to check if string or not
object_id = None

model = torchvision.models.mobilenet_v3_small(pretrained=True)
model.eval()


def detection(image):
    transforms = torchvision.transforms.Compose([
        # torchvision.transforms.ToPILImage(),
        torchvision.transforms.Resize((280, 280)),
        torchvision.transforms.ToTensor()
    ])

    transformed_image = transforms(image)
    transformed_image = transformed_image.reshape(1, 3, 280, 280)

    result = model(transformed_image)

    interesting_idxs = [504, 587, 673, 761, 898, 999]
    scores = result[0].detach().numpy()[interesting_idxs]

    max_idx = np.argmax(scores)
    if scores[max_idx] > 4:
        return max_idx
    else:
        return None

def camerasample(seconds = 1.0):

    global STOP
    global FRAME
    global object_id


    t = threading.Timer(float(seconds), camerasample)
    t.start()
    
    if FRAME != 'empty':

        det = detection(FRAME)
        object_id = det
        
    if STOP:
        t.cancel()



# This runs on a separate thread and overwrites continously the FRAME global variable. 

def webcam():
    global STOP
    global FRAME

    cv2.namedWindow("cozmo camera")
    vc = cv2.VideoCapture(0)

    if vc.isOpened(): # try to get the first frame
        rval, frame = vc.read()
    else:
        rval = False

    while rval:
        cv2.imshow("cozmo camera", frame)

        rval, frame = vc.read()

        cv2_im = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
        pil_im = Image.fromarray(cv2_im)

        FRAME = pil_im

        key = cv2.waitKey(20)

        if key == 27: # exit on ESC
            STOP = True
            break
    

    vc.release()
    cv2.destroyWindow("cozmo camera")