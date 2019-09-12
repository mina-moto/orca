#coding: UTF-8
# Numpy
import numpy as np
# Chainer
import chainer
import math
import random
import json
import time
import argparse
from chainer import Chain, Variable
from chainer import optimizers
import chainer.functions as F
import chainer.links as L
from chainer import serializers
import collections as cl #collectionsをインポート
import glob
from statistics import mean
'''
天候からネガポジ予測
'''
class wether_to_np_net(Chain):
    # インスタンス生成，model=AutoEncoder()とか
    def __init__(self):
        # インスタンス変数
        self.input_num=9
        self.output_data=[]
        super(wether_to_np_net, self).__init__(
            l1 = L.Linear(self.input_num, 7),
            bn1 = L.BatchNormalization(7),
            l2 = L.Linear(7,3),#出力
            bn2 = L.BatchNormalization(3),
            l3 = L.Linear(3,2),#出力
            bn3 = L.BatchNormalization(2)
        )
    # 活性化関数で推定，
    def forward(self,input_data):
        # print(input_data)
        h=F.relu(self.l1(input_data))
        # print("h1")
        # print(h)
        h=F.relu(self.l2(h))
        # print("h2")
        # print(h)
        h=F.relu(self.l3(h))
        # print("h3")
        # print(h)
        # h = self.bn3(h,finetune=False)
        self.output_data=F.softmax(h)
        # print("self.output_data")
        print(self.output_data.data)
        return self.output_data.data

    # 活性化関数で推定，損失関数の計算
    def loss(self,input_data,label):
        # print(input_data)
        h=F.relu(self.l1(input_data))
        h = self.bn1(h, finetune=False)
        h=F.relu(self.l2(h))
        h = self.bn2(h,finetune=False)
        h=F.relu(self.l3(h))
        h = self.bn3(h,finetune=False)
        self.output_data=F.softmax(h)
        # print(self.output_data.data)

        def cross_entropy(predictions, targets, epsilon=1e-12):
            """
            Computes cross entropy between targets (encoded as one-hot vectors)
            and predictions.
            Input: predictions (N, k) ndarray
                   targets (N, k) ndarray
            Returns: scalar
            """
            predictions = np.clip(predictions, epsilon, 1. - epsilon)
            N = predictions.shape[0]
            ce = -np.sum(targets*np.log(predictions+1e-9))/N
            return ce
        # print("self.output_data")
        # print(self.output_data.data)
        # print("label")
        # print(label)
        loss=cross_entropy(np.array(self.output_data.data), label, epsilon=1e-12)
        # # loss=F.softmax_cross_entropy(h,label)
        # loss=F.softmax_cross_entropy(h,label)
        # loss=F.mean_squared_error(self.output_data, label)
        loss=Variable(np.array(loss))
        # print(loss)
        return loss


# 正規化のためのデータ読み込み
def read_maxmin():
    f = open('./outputMaxMin.json', 'r')
    outputMaxMin = json.load(f)
    f.close()
    return outputMaxMin
def normalization_data(data,max,min):
    if max==min:#一応0除算回避
        return 0
    return (data-min)/(max-min)
# 入力データ正規化
def normalization_input_data(input_data):
    outputMaxMin=read_maxmin()
    max_data=list(outputMaxMin["max"][0].values())[1:]
    min_data=list(outputMaxMin["min"][0].values())[1:]
    normalization_input_data=[]
    for i,input in enumerate(input_data):
        normalization_input_data.append(normalization_data(input,max_data[i],min_data[i]))
    return normalization_input_data

def learn(model,day_input_str_list,day_list,input_data_all,days_pn,user="all",iteration=500,batch_size=5):
    # # Setup optimizer
    optimizer = optimizers.Adam()
    optimizer.setup(model)
    start=time.time()#学習開始時刻
    for e in range(1,iteration+1):
        random.shuffle(day_input_str_list)
        # 1iterateにつき10個
        batch_day_list=day_input_str_list[0:batch_size]
        #print("****************************************")
        # 入力データ生成
        input_data=[]
        for day,input in input_data_all.items():
            if day.replace("-","/") in batch_day_list:
                #print(day)
                input_data.append(input)
                if len(input_data)>=batch_size:
                    break
        #print("========================================")
        # モデルに入力するデータ
        input_data=np.array(input_data,dtype=np.float32)
        # 正解データ生成
        label_data=[]
        for day,pn in days_pn.items():
            if day.replace("-","/") in batch_day_list:
                #print(day)
                label_data.append([pn,1-pn])
                # 数が同じになればbreak
                if len(label_data)>=batch_size:
                    break
        #print("++++++++++++++++++++++++++++++++++++++++")
        # 正解データ
        label_data=np.array(label_data,dtype=np.float32)
        model.cleargrads()
        loss = model.loss(input_data,label_data)
        loss.backward()#逆誤差伝搬
        optimizer.update()# 勾配の更新
        # print(str(e)+"th loss:"+str(loss.data))
    print(str(iteration)+"th loss:"+str(loss.data))
    serializers.save_npz("./model/"+str(user)+".npz", model) # npz形式で書き出し
    t=time.time()-start#かかった時間
    print("time:"+str(t)+"sec")

def validation (user="all"):
    day_list=[]
    with open("./day_list_for_validation/"+user+"_day_list.txt", 'r') as f:
        day_list = [s.strip() for s in f.readlines()]
    print("length of day_list:"+str(len(day_list)))
    model=wether_to_np_net()
    file_list=glob.glob("./model/*")
    if "./model/"+user+".npz" in file_list:
        serializers.load_npz("./model/"+user+".npz", model)
    else:
        return 0.5
    optimizer = optimizers.Adam()
    optimizer.setup(model)
    # 正解データ読み込み
    f = open('./result/result_pn.json', 'r')
    pn_json = json.load(f)
    f.close()
    # 入力データ読み込み
    f = open('./output.json', 'r')
    input_data_json = json.load(f)
    f.close()


    err=[]
    err2=[]
    for input_data in input_data_json["list"]:
        if input_data["day"].replace("-","/") in day_list:
            day=input_data.pop("day").replace("-","/")
            #print(input_data)
            in_list=list(input_data.values())
            #print(in_list)
            # 入力データ正規化
            # in_list=normalization_input_data(in_list)
            in_list=np.array([in_list],dtype=np.float32)
            res=model.forward(in_list)
            res=res[0][0]
            ans=pn_json[user][day]
            err.append((ans-res)**2)
            err2.append(abs(ans-res))
            #print(day+" res"+str(res)+" ans:"+str(ans))
    #print("平均二乗誤差:"+str(mean(err)))
    print("平均絶対誤差:"+str(mean(err2)))
    return mean(err)



# 引数のユーザ学習しモデル保存，user=allで全データで学習
def learn_user(user="all",iteration=100,batch_size=50):
    # user_name=""
    print(user)
    model=wether_to_np_net()
    # 入力データ読み込み
    f = open('./output.json', 'r')
    input_data_json = json.load(f)#list
    f.close()
    # 正解データ煮込み
    f = open('./result/result_pn.json', 'r')
    pn_json = json.load(f)
    # あるユーザの日付ごとのネガポジ正解値
    days_pn=pn_json[user]
    f.close()
    # ユーザの使えるデータの日付のリスト．/の方
    day_list=list(days_pn.keys())
    # 日付の文字列の形式をinput_data_listに合わせたもの，-の方
    day_input_str_list = list(map(lambda day: day.replace("-","/"), day_list))
    day_input_str_list_tmp=[]
    # 天気の全入力データ
    input_data_all=cl.OrderedDict()
    for input in input_data_json["list"]:
        input_value=[]#日付以外の要素のリスト
        #print(input["day"])
        if input["day"].replace("-","/") in day_input_str_list:
            day_input_str_list_tmp.append(input["day"].replace("-","/"))
            for k,v in input.items():
                if k!="day":
                    input_value.append(v)#ある日付の全値
            day=input["day"]
            input_data_all[day]=input_value
    day_input_str_list=day_input_str_list_tmp

    len_day_list=len(day_input_str_list)
    random.shuffle(day_input_str_list)
    validation_list=day_input_str_list[:len_day_list//5]
    day_input_str_list=day_input_str_list[len_day_list//5:]
    with open("./day_list_for_validation/"+user+"_day_list.txt", 'wt') as f:
        for element in validation_list:
            f.write(element+"\n")
    learn(model,day_input_str_list,day_list,input_data_all,days_pn,user,iteration,batch_size)
    validation(user)

# ネガポジ判定結果のある全ユーザ学習し保存．
if __name__ == "__main__":
    f = open('./result/result_pn_reaction.json', 'r')
    pn_json = json.load(f)
    user_list=list(pn_json.keys())
    cnt=0
    for user in user_list:
        if 250>len(list(pn_json[user].keys())):
            continue
        learn_user(user)
        cnt+=1
        if cnt>5:
            break
    # learn_user("")
