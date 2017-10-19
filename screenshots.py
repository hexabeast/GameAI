#!env2/bin/python
# encoding: utf-8

import numpy as np
import time

import mss
from PIL import Image


FPS = 20
num = 0

box = (200,200,600,600)



def getscreenshot(dim=box):
    with mss.mss() as sct:

        monitor = sct.monitors[1]
        curtime = time.clock()

        left = monitor['left']+dim[0]
        top = monitor['top']+dim[1]
        width = dim[2]
        height = dim[3]
        bbox = {'left':left, 'top':top, 'width':width, 'height':height}

        sct_img = sct.grab(bbox)
        return sct_img

def getscreenPIL(dim=box, reduction=1):
    sct_img = getscreenshot(dim)
    arr = np.array(sct_img)[::reduction,::reduction]
    arr[:,:,3] = 255
    temp = arr[:,:,0].copy()
    arr[:,:,0] = arr[:,:,2]
    arr[:,:,2] = temp
    return Image.fromarray(arr)
    #return Image.frombytes('RGB', sct_img.size, sct_img.rgb)

def getscreenNP(dim=box, reduction=1):
    sct_img = getscreenshot(dim)
    arr = np.array(sct_img)[::reduction,::reduction]
    arr[:,:,3] = 255
    temp = arr[:,:,0].copy()
    arr[:,:,0] = arr[:,:,2]
    arr[:,:,2] = temp
    return arr[:,:,:3]


#getscreenPIL().save('data/img/'+str(42)+".png")