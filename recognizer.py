import cv2
import numpy as np
import subprocess

from pynput.mouse import Button, Controller

def getDisplaySize():
    cmd = ['xrandr']
    cmd2 = ['grep', '*']
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    p2 = subprocess.Popen(cmd2, stdin=p.stdout, stdout=subprocess.PIPE)
    p.stdout.close()

    return [int(i) for i in str(p2.communicate()[0]).split()[1].split("x")]

mouse = Controller()

(sx, sy) = getDisplaySize()
(camx, camy) = (320, 250)

upper_blue = np.array([179, 255, 255])
lower_blue = np.array([103, 122, 78])

cap = cv2.VideoCapture(0)

kernelOpen = np.ones((5, 5))
kernelClose = np.ones((20, 20))

pinchFlag = 0

while True:
    _, frame = cap.read()
    frame = cv2.resize(frame,(320, 250))

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    mask = cv2.inRange(hsv, lower_blue, upper_blue)
    
    maskOpen = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernelOpen)
    maskClose = cv2.morphologyEx(maskOpen, cv2.MORPH_CLOSE, kernelClose)

    maskFinal = maskClose
    _, conts, h = cv2.findContours(maskFinal.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    if len(conts) == 2:
        if pinchFlag == 1:
            pinchFlag = 0
            mouse.release(Button.left)

        x1, y1, w1, h1=cv2.boundingRect(conts[0])
        x2, y2, w2, h2=cv2.boundingRect(conts[1])
        
        cv2.rectangle(frame, (x1, y1),(x1 + w1, y1 + h1), (255, 0, 0), 2)
        cv2.rectangle(frame, (x2, y2), (x2 + w2, y2 + h2), (255, 0, 0), 2)

        cx1 = int(x1 + w1/2)
        cy1 = int(y1 + h1/2)
        
        cx2 = int(x2 + w2/2)
        cy2 = int(y2 + h2/2)

        cx = int((cx1 + cx2) / 2)
        cy = int((cy1 + cy2) / 2)

        cv2.line(frame, (cx1, cy1), (cx2, cy2), (255, 0, 0), 2)
        cv2.circle(frame, (cx, cy), 2, (0 , 0 , 255) , 2)

        mouseLoc = (int(sx - (cx * sx / camx)), int(cy * sy / camy))
        mouse.position = mouseLoc 

    elif len(conts) == 1:
        x, y, w, h = cv2.boundingRect(conts[0])

        if pinchFlag == 0:
            pinchFlag = 1
            mouse.press(Button.left)

        cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)

        cx = int(x + w / 2)
        cy = int(y + h / 2)

        cv2.circle(frame, (cx, cy), int((w + h) / 4), (0, 0, 255), 2)

        mouseLoc = int(sx - (cx * sx / camx)), int(cy * sy / camy)
        mouse.position = mouseLoc

    cv2.imshow("cap", frame)
    if cv2.waitKey(1) == 27:
        break

cap.release()
cv2.destroyAllWindows()
