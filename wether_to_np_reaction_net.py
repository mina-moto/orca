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
from sklearn.metrics import log_loss
'''
天候からネガポジ予測，正解データ=チャットのネガポジ+reactionのネガポジ
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
            l2 = L.Linear(7,3),
            bn2 = L.BatchNormalization(3),
            l3 = L.Linear(3,2),#出力
            bn3 = L.BatchNormalization(2)
        )
    # 活性化関数で推定，
    def forward(self,input_data):
        # print(input_data)
        h=F.relu(self.l1(input_data))
        h=F.relu(self.l2(h))
        # print(h)
        self.output_data=F.softmax(h)
        # print(self.output_data.data)
        return self.output_data.data

    # 活性化関数で推定，損失関数の計算
    def loss(self,input_data,label):
        # loss=F.mean_squared_error(self.forward(input_data), label)
        h=self.l1(input_data)
        h = self.bn1(h, finetune=False)
        h=self.l2(h)
        h = self.bn2(h,finetune=False)
        h=self.l3(h)
        h = self.bn3(h,finetune=False)
        self.output_data=F.softmax(h)
        print(self.output_data.data)
        print(label)
        # print(label)
        # loss=chainer.cross_entropy(self.output_data.data, label)
        loss=log_loss(self.output_data.data, label.data)
        print(loss)
        return loss

# 引数のユーザ学習しモデル保存，user=allで全データで学習
def learn_user(user="all",iteration=100,batch_size=5):
    # user_name=""
    print(user)
    model=wether_to_np_net()
    # 入力データ読み込み
    f = open('./output.json', 'r')
    input_data_json = json.load(f)#list
    f.close()
    # 天気の全入力データ
    input_data_all=cl.OrderedDict()
    for input in input_data_json["list"]:
        input_value=[]#日付以外の要素のリスト
        for k,v in input.items():
            if k!="day":
                input_value.append(v)#ある日付の全値
        day=input["day"]
        input_data_all[day]=input_value
    # 正解データ煮込み
    f = open('./result/result_pn.json', 'r')
    pn_json = json.load(f)
    # あるユーザの日付ごとのネガポジ正解値
    days_pn=pn_json[user]
    f.close()
    # ユーザの使えるデータの日付のリスト．/の方
    day_list=list(days_pn.keys())
    # 日付の文字列の形式をinput_data_listに合わせたもの，-の方
    day_input_str_list = list(map(lambda day: day.replace("/","-"), day_list))

    # # Setup optimizer
    optimizer = optimizers.Adam()
    optimizer.setup(model)
    start=time.time()#学習開始時刻
    for e in range(1,iteration+1):
        random.shuffle(day_list)
        #1iterateにつき10個
        batch_day_list=day_list[0:batch_size]

        # 入力データ生成
        input_data=[]
        for day,input in input_data_all.items():
            if day in day_input_str_list:
                input_data.append(input)
                if len(input_data)>=batch_size:
                    break

        # モデルに入力するデータ
        input_data=np.array(input_data,dtype=np.float32)

        # 正解データ生成
        label_data=[]
        for day,pn in days_pn.items():
            if day in batch_day_list:
                label_data.append([pn,1-pn])
                # 数が同じになればbreak
                if len(label_data)>=batch_size:
                    break
        # 正解データ
        label_data=np.array(label_data,dtype=np.float32)
        model.cleargrads()
        loss = model.loss(input_data,label_data)
        loss.backward()#逆誤差伝搬
        optimizer.update()# 勾配の更新
        # print(str(e)+"th loss:"+str(loss.data))
    print(str(iteration)+"th loss:"+str(loss.data))
    serializers.save_npz("./add_reaction_model/"+str(user)+".npz", model) # npz形式で書き出し
    t=time.time()-start#かかった時間
    print("time:"+str(t)+"sec")

# チャットのネガポジ+reactionのネガポジ判定結果のある全ユーザ学習し保存．
if __name__ == "__main__":
    f = open('./result/result_pn_reaction.json', 'r')
    pn_json = json.load(f)
    user_list=list(pn_json.keys())
    for user in user_list:
        if 100>len(list(pn_json[user].keys())):
            continue
        learn_user(user)
