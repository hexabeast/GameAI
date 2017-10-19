#!env2/bin/python

import os
import threading
import time
import uinput

use_controller=True
generate_controller = True
mirror = False

pause = False


layout = {
    "a": 20,
    "z": 26,
    "e": 8,
    "r": 21,
    "t": 23,
    "q": 4,
    "s": 22,
    "d": 7,
    "f": 9,
    "w": 29,
    "x": 27,
    "c": 6,
    "up": 82,
    "down": 81,
    "left": 80,
    "right": 79,
    "shift": 225,
    "ctrl": 224,
    "space": 44
}

inv_layout = {v: k for k, v in layout.items()}

layout_xbox_button = {
    "a": 0,
    "b": 1,
    "x": 2,
    "y": 3,
    "lb": 4,
    "rb": 5,
    "select": 6,
    "start": 7,
    "xbox": 8,
    "left_press": 9,
    "right_press": 10,
}

layout_xbox_analog = {
    "Lpad_hor": 0,
    "Lpad_ver": 1,
    "Rpad_hor": 3,
    "Rpad_ver": 4,
    "LT": 2,
    "RT": 5,
    "Cross_hor": 6,
    "Cross_ver": 7,
}

xbox_activations = {
    "a": 0,
    "b": 0,
    "x": 0,
    "y": 0,
    "lb": 0,
    "rb": 0,
    "select": 0,
    "start": 0,
    "xbox": 0,
    "left_press": 0,
    "right_press": 0,
    "Lpad_hor": 0,
    "Lpad_ver": 0,
    "Rpad_hor": 0,
    "Rpad_ver": 0,
    "LT": -50,
    "RT": -50,
    "Cross_hor": 0,
    "Cross_ver": 0,
}

inv_layout_xbox_button = {v: k for k, v in layout_xbox_button.items()}
inv_layout_xbox_analog = {v: k for k, v in layout_xbox_analog.items()}

xbox_uinput = {
    "a": uinput.BTN_A,
    "b": uinput.BTN_B,
    "x": uinput.BTN_X,
    "y": uinput.BTN_Y,
    "lb": uinput.BTN_TL,
    "rb": uinput.BTN_TR,
    "select": uinput.BTN_SELECT,
    "start": uinput.BTN_START,
    "xbox": uinput.BTN_MODE,
    "left_press":  uinput.BTN_THUMBL,
    "right_press":  uinput.BTN_THUMBR,

    "LT": uinput.ABS_Z + (-50, 50, 0, 0),
    "RT": uinput.ABS_RZ + (-50, 50, 0, 0),
    "Lpad_hor": uinput.ABS_X + (-50, 50, 0, 0),
    "Lpad_ver": uinput.ABS_Y + (-50, 50, 0, 0),
    "Rpad_hor": uinput.ABS_RX + (-50, 50, 0, 0),
    "Rpad_ver": uinput.ABS_RY + (-50, 50, 0, 0),
    "useless1": uinput.ABS_HAT0X + (00, 50, 0, 0),
    "useless2": uinput.ABS_HAT0Y + (00, 50, 0, 0),
}
inv_xbox_uinput = {v: k for k, v in xbox_uinput.items()}


inputlist = []

lock = threading.Lock()

dev = None
if generate_controller:
    events = list(xbox_uinput.values())
    dev = uinput.Device(events,
                        name="Microsoft X-Box 360 pad",
                        bustype=0x0003,
                        vendor=0x046d,
                        product=0x028e,
                        version=0x0114)
    time.sleep(0.2)

def getPause():
    global pause
    if pause:
        pause = False
        return True
    else:
        return False

def press_button(id,state):
    dev.emit(xbox_uinput[id], state)

def use_analog(id,state):
    dev.emit(xbox_uinput[id][:2], state)

def getInputs():
    global inputlist,lock

    st = " ".join(inputlist)
     
    lock.acquire()
    inputlist = []
    lock.release()

    return st

def read_keyboard(inputlist,lock):
    with open("/dev/input/event5", 'rb') as device:
        while True:
            bs = device.read(8)
            tab = [elem for elem in (bs)]
            key = -1
            act = -1
            if tab[0] == 4 and tab[1] == 0 and tab[2] == 4:
                key = tab[4]

            if tab[0] == 1 and tab[1] == 0 and tab[3] == 0:
                act = tab[4]

            if key != -1:
                val = key
                if val in inv_layout:
                    val = inv_layout[val]
                lock.acquire()
                inputlist.append(str(val))
                lock.release()

            if act == 0 or act == 1:
                lock.acquire()
                val = '-'
                if act == 1:
                    val = '+'
                inputlist[-1]+=val
                lock.release()

            if __name__ == '__main__':
                if act != -1 and act != 2:
                    print("act:"+str(act))
                if key != -1:
                    print("act:"+str(key))


def read_controller(inputlist,lock):
    global xbox_activations,pause
    with open('/dev/input/js0', 'rb') as device:
        while True:
            bs = device.read(8)
            tab = [elem for elem in (bs)]
            key = -1
            act = -1

            printmode = 0

            if __name__ == '__main__':
                printmode = 2

            if tab[6] == 1:
                key = tab[7]
                act = tab[4]

                inputlist.append(inv_layout_xbox_button[key]+':'+str(act))

                xbox_activations[inv_layout_xbox_button[key]] = act

                if inv_layout_xbox_button[key]  == "right_press" and act == 1:
                    pause = True


                if mirror:
                    press_button(inv_layout_xbox_button[key],act)

                if printmode>0:
                    print(inv_layout_xbox_button[key]+": "+str(act))
                    

            if tab[6] == 2:
                key = tab[7]
                act = tab[5]
                if act>127:
                    act -= 256
                act+=128
                act = int(act*100/255)-50

                lock.acquire()
                inputlist.append(inv_layout_xbox_button[key]+':'+str(act))
                lock.release()

                xbox_activations[inv_layout_xbox_analog[key]] = act

                if mirror:
                    use_analog(inv_layout_xbox_analog[key],act)

                if printmode>1:
                    print(inv_layout_xbox_analog[key]+": "+str(act))

            '''
                    val = inv_layout[val]
                lock.acquire()
                inputlist.append(str(val))
                lock.release()

            if act == 0 or act == 1:
                lock.acquire()
                val = '-'
                if act == 1:
                    val = '+'
                inputlist[-1]+=val
                lock.release()

            if tab[0] == 4 and tab[1] == 0 and tab[2] == 4:
                key = tab[4]

            if tab[0] == 1 and tab[1] == 0 and tab[3] == 0:
                act = tab[4]

            if key != -1:
                val = key
                if val in inv_layout:
            if __name__ == '__main__':
                if act != -1 and act != 2:
                    print("act:"+str(act))
                if key != -1:
                    print("act:"+str(key))  
            '''
def readinputs():
    global inputlist,lock
    if not use_controller:
        read_keyboard(inputlist,lock)
    else:
        read_controller(inputlist,lock)
    


def start_thread(loc):
    global lock
    lock = loc
    t1 = threading.Thread(target=readinputs, args=[])
    t1.start()

def main():
    readinputs()



if __name__ == '__main__':
    main()
