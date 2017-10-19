#!env2/bin/python
from models import alexnet2,alexnet2backup
import numpy as np
import data_process
import os

n_bigbatch = 1000
nmodel = "classic_balanced"

timesteps = 1

width = 200
height = 150
lr = 5e-5
epochs = 5
bigbatch_size = 5000
model_name = 'RocketLeagueAI-{}-{}-{}-epochs.model'.format(nmodel,'alexnet2',10)

alex = alexnet2backup



if __name__ == "__main__":

    model = alex(height,width,lr,9,timesteps)
    if os.path.isfile('models/'+model_name+".meta"):
        model.load('models/'+model_name)#'RocketLeagueAI-{}-{}-{}-epochs.model'.format("0.001",'alexnet2',20))
    else:
        input("No save for this model /!\\")
    valid_size = 2000


    cur_n = 0
    while cur_n <= n_bigbatch:
        train_data,test_data = data_process.get_batches(bigbatch_size,valid_size,timesteps,balance=True)
        for i in range(len(train_data)):
            cur_n+=1
            if cur_n >n_bigbatch:
                break
            train_data[i-1].unload()
            train_data[i].load()
            train = train_data[i].content

            print(cur_n)
            
            X = np.array([i[0] for i in train]).reshape(-1,height,width,3)

            Y = np.array([i[1] for i in train])
            print(Y.shape)

            print(X.shape)

            test_X = np.array([i[0] for i in test_data]).reshape(-1,height,width,3)
            test_Y = np.array([i[1] for i in test_data])


            model.fit({'input': X}, {'targets': Y}, n_epoch=epochs,validation_set=({'input': test_X}, {'targets': test_Y}),
            snapshot_step=500,show_metric=True,run_id=model_name)#,batch_size=timesteps)

            model.save('models/'+model_name)