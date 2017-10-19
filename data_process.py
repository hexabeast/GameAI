#!env2/bin/python
from PIL import Image
import numpy as np
import os
import random

imageprocess = True
npyprocess = True

sessions = [0,1,2,3]

length = 0

processed_path = "processed_data2/"
datafolder = "fdata"

inputdata = {
    "a": [],
    "b": [],
    "x": [],
    "y": [],
    "lb": [],
    "rb": [],
    "select": [],
    "start": [],
    "xbox": [],
    "left_press": [],
    "right_press": [],
    "Lpad_hor": [],
    "Lpad_ver": [],
    "Rpad_hor": [],
    "Rpad_ver": [],
    "LT": [],
    "RT": [],
    "Cross_hor": [],
    "Cross_ver": [],
}
order_inputs = ["a","b","x","LT","RT","Lpad_hor_left","Lpad_hor_right","Lpad_ver_up","Lpad_ver_down"]

def count_nonzeros(liste):
    l = len(liste)
    s=0
    for i in range(l):
        if liste[i]!=0:
            s+=1
    return s/l


if os.path.isfile(processed_path+"processed_input.npy"):
    loaded_inputs = np.load(processed_path+"processed_input.npy")
    length = len(loaded_inputs)
    print(length)

class ImageBatch:
    def __init__(self,numbers):
        self.numbers = numbers
        self.content = None
    
    def load(self):
        print("Loading batch into memory...")
        cont = []
        screename2 = lambda x : processed_path+"screen_"+str(x)+".npz"

        i = 0
        for num in self.numbers:
            i+=1
            print(i)
            with np.load(screename2(num)) as arrim:
                cont.append((np.array(arrim['arr_0']),loaded_inputs[num]))
                del arrim.f
                arrim.close()

        self.content = cont
        
        print("Done loading batch !")


    def unload(self):
        del self.content
        self.content = None
        


def get_batches(bigbatch_size,valid_size,steps,balance=False):

    train_size = length-valid_size
    repartition2 = list(range(train_size,length))

    
    repartition = list(range(train_size))
    if balance:
        ###BALANCE>
        handicap = [0 for i in range(train_size)]
        probs = np.zeros((9,))
        for _ in range(5):
            for i in repartition:
                for j in range(9):
                    if loaded_inputs[i][j] != 0:
                        probs[j]+=1

            probs/=train_size
            #print(repartition)
            print(probs)
            print(len(repartition))

            current = 0 
            everyone = []    
            while current<len(repartition):
                score = 0
                i = repartition[current]
                for j in range(9):
                    score-=0.5
                    if loaded_inputs[i][j] != 0:
                        score += abs(loaded_inputs[i][j]-probs[j])**2
                    else:
                        score += probs[j]**2
                score/=9
                score-=handicap[i]
                everyone.append((score,i))
                #print(score)
                #print(loaded_inputs[i])
                current+=1
                '''
                if random.random()<disappear:
                    repartition.pop(current)
                elif random.random()>disappear:
                    repartition.insert(current,i)
                    current+=2'''
            everyone.sort()
            repartition = []
            for j in range(len(everyone)):
                one = everyone[j][1]
                good = float(j)/len(everyone)

                activ = 0
                if random.random()<good*2:
                    repartition.append(one)
                    activ+=1
                if random.random()<good/2:
                    repartition.append(one)
                    activ+=1
                if 0 == activ:
                    handicap[one]-=0.02
                elif activ == 2:
                    handicap[one]+=0.02
            #input()
            ###<BALANCE

    train_size = len(repartition)

    train_size-=train_size%steps
    #repartition = list(range(train_size))
    
    
    assert bigbatch_size%steps == 0 and valid_size%steps == 0

    reparlist = [[repartition[i+j*steps] for i in range(steps)] for j in range(train_size//steps)]
    #print(reparlist)
    random.shuffle(reparlist)
    #print(reparlist)
    repartition = [reparlist[i//steps][i%steps] for i in range(train_size)]
    #print(repartition)
    
    i = 0
    batches = []
    while i+bigbatch_size<train_size:
        batch = ImageBatch(repartition[i:i+bigbatch_size])
        batches.append(batch)
        i+=bigbatch_size

    valid = []

    i=0
    for num in repartition2:
        i+=1
        with np.load(processed_path+"screen_"+str(num)+".npz") as arrim:
            valid.append((np.array(arrim['arr_0']),loaded_inputs[num]))
            del arrim.f
            arrim.close()

    return batches,valid

def get_all(limit = -1):
    repartition = list(range(length))
    random.shuffle(repartition)

    i = 0
    
    cont = []
    screename2 = lambda x : processed_path+"screen_"+str(x)+".npz"

    for num in repartition:
        i+=1
        if limit>=0 and i>limit:
            break
        print(i)
        arrim = np.load(screename2(num))
        cont.append((arrim,loaded_inputs[num]))

    content = cont
    return content


if __name__ == '__main__':
    curp = 0
    oldp = 0
    length = 0

    for n in range(len(sessions)):
        f = open(datafolder+'/session_'+str(sessions[n])+'/inputs.txt','r')
        lines = f.readlines()
        plines = []
        length += len(lines)
        for line in lines:
            splitted = line.split()
            for elem in splitted:
                resplitted = elem.split(":")
                inputdata[resplitted[0]].append(int(resplitted[1]))

        if imageprocess:

            screename = lambda x : datafolder+'/session_'+str(sessions[n])+'/screenshot_'+str(x)+'.png'
            prevarrim = None

            p = curp-oldp
            while os.path.isfile(screename(p)):
                
                if p%100==0:
                    print(curp)
                
                imexist = os.path.isfile(processed_path+"screen_"+str(curp)+".png")
                npexist = os.path.isfile(processed_path+"screen_"+str(curp)+".npz")

                if not (imexist and npexist):
                    im = Image.open(screename(p))
                    arrim = np.asarray(im)
                    arrim = np.copy(arrim)
                    arrim.flags.writeable = True
                    if prevarrim is not None:
                        '''for i in range(len(arrim)):
                            for j in range(len(arrim[0])):
                                for k in range(3):
                                    arrim[i,j,k] = int(arrim[i,j,k]*0.75+prevarrim[i,j,k]*0.25)
                        '''
                        arrim[:] = arrim[:]*0.6+prevarrim[:]*0.4

                    im = Image.fromarray(arrim)
                    prevarrim = arrim
                    if not imexist:
                        im.save(processed_path+"screen_"+str(curp)+".png")

                    arrim = arrim[:,:,:3].astype(float)
                    #arrim/=255
                    if not npexist:
                        np.savez_compressed(processed_path+"screen_"+str(curp)+".npz",arrim)

                curp+=1
                p = curp-oldp

            oldp = curp
                
        '''
        if npyprocess:
            p=1
            screename2 = lambda x : processed_path+"screen_"+str(x)+".png"
            nbatch = 0
            training_data = []
            while os.path.isfile(screename2(p)):
                if p%100==0:
                    print(p)
                im = Image.open(screename2(p))
                arrim = np.asarray(im)
        '''
            



    for k, v in inputdata.items():
        inputdata[k] = np.array(v).astype(float)
        

    inputdata["LT"][:]+=50
    inputdata["RT"][:]+=50

    inputdata["LT"][:]/=100
    inputdata["RT"][:]/=100
    inputdata["Lpad_hor"][:]/=50
    inputdata["Lpad_ver"][:]/=50

    inputdata["Rpad_hor"][:]/=50
    inputdata["Rpad_ver"][:]/=50

    inputdata["Lpad_hor_left"] = np.array([max(0,-2*x) for x in inputdata["Lpad_hor"]])
    inputdata["Lpad_hor_right"] = np.array([max(0,2*x) for x in inputdata["Lpad_hor"]])

    inputdata["Lpad_ver_up"] = np.array([max(0,-2*x) for x in inputdata["Lpad_ver"]])
    inputdata["Lpad_ver_down"] = np.array([max(0,2*x) for x in inputdata["Lpad_ver"]])


    for k, v in inputdata.items():
        inputdata[k][v>0.5] = 1
        inputdata[k][v<-0.5] = -1
        inputdata[k][np.abs(v)<0.5] = 0
   
        
    

    for k, v in inputdata.items():
        print(k+": "+str("%.2f" %(count_nonzeros(inputdata[k])*100)))

    input_processed = np.array([[inputdata[j][i] for j in order_inputs] for i in range(length)])

    np.save(processed_path+"processed_input.npy",input_processed)
