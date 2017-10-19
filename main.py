#!env2/bin/python

import os
import screenshots
import inputs
import time
import threading
import numpy as np
import data_process
from models import alexnet2,alexnet2backup
import training

lock = threading.Lock()

timesteps = training.timesteps

instantdelayframes = 1
instantpress = {
    "a":0
}

FPS = 15
box = (68,52,800,600)

play = True

if play:
    inputs.use_controller = False

'''
width = 200
height = 150
lr = 2e-4
epochs = 10
nmodel = 3
model_name = training.model_name
'''

model = None

if play:
    model = training.alex(training.height,training.width,training.lr,9,training.timesteps)
    model.load("models/"+training.model_name)

timeimgs = []

def main():
    
    i = 0
    directory = os.path.dirname("data/session_"+str(i)+"/")
    while os.path.exists(directory):
        i+=1
        directory = os.path.dirname("data/session_"+str(i)+"/")

    inputs.start_thread(lock)
    f = None
    if not play:
        os.makedirs(directory)
        f = open(os.path.join(directory,"inputs.txt"),'w')
    
    n = 0
    input("Press enter to begin")
    while True:
        if inputs.use_controller:
            if inputs.getPause() or n == 0:
                while not inputs.getPause():
                    time.sleep(0.01)

        curtime = time.clock()
        oldimg = None
        ########################
        if not play:
            path = os.path.join(directory,"screenshot_"+str(n)+".png")
            screenshots.getscreenPIL(box,4).save(path)
            if n>0:
                st = ""
                if inputs.use_controller:
                    st = [key+":"+str(val) for key, val in inputs.xbox_activations.items()]
                    st = " ".join(st)
                else:
                    st = inputs.getInputs()

                    
                f.write(st+'\n')
            print(path)
        else:
            img = screenshots.getscreenNP(box,4)
            if oldimg != None:
                img[:] = img[:]*0.6+oldimg[:]*0.4

            timeimgs.append(img)

            if len(timeimgs)>timesteps:
                timeimgs.pop(0)

            oldimg = img

            if len(timeimgs) == timesteps:
                arri = np.array(timeimgs)
                '''if len(arri.shape) == 4:
                    arri = arri.reshape(1,arri.shape[0],arri.shape[1],arri.shape[2],arri.shape[3])'''
                prediction = model.predict(arri)[-1] #
                prediction[0]*=2
                prediction[1]*=3
                prediction[3]*=2
                prediction[4]*=3
                prediction[5]*=8
                prediction[6]*=8
                prediction[7]*=10
                prediction[8]*=10

                pred_hor = prediction[6]-prediction[5]

                prediction = np.clip(prediction,0,1)

                print(prediction)
                pred_hor = np.clip(pred_hor,-1,1)
                pred_hor = np.around(pred_hor)
                moves = np.around(prediction).astype(int)


                if instantpress["a"]>0:
                    instantpress["a"]-=1
                    if instantpress["a"] == 0:
                        inputs.press_button("a",0)
                else:
                    a_value = int(moves[0])
                    inputs.press_button("a",a_value)
                    if a_value == 1:
                        instantpress["a"] = instantdelayframes
                inputs.press_button("b",int(moves[1]))
                inputs.press_button("x",int(moves[2]))
                inputs.use_analog("LT",int(moves[3]*100-50))
                inputs.use_analog("RT",int(moves[4]*100-50))
                '''if moves[5]>moves[6]:
                    inputs.use_analog("Lpad_hor",-int(moves[5]*50))
                else:
                    inputs.use_analog("Lpad_hor",int(moves[6]*50))
                '''
                inputs.use_analog("Lpad_hor",int(pred_hor*50))
                if moves[7]>moves[8]:
                    inputs.use_analog("Lpad_ver",-int(moves[7]*50))
                else:
                    inputs.use_analog("Lpad_ver",int(moves[8]*50))
            

        ########################

        timeleft = curtime + 1/FPS - time.clock()
        if timeleft>0:
            time.sleep(timeleft)
        else:
            print("/!\\ too slow /!\\")
            print(timeleft)
        
        n+=1




if __name__ == '__main__':
    main()
