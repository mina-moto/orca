#coding: UTF-8
# Numpy
import numpy as np
import glob
# Chainer
import chainer
import math
import json
import argparse
import datetime
import weather_info
from chainer import optimizers
from chainer import serializers
from wether_to_np_net import wether_to_np_net

print(datetime.date.today())
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

# 指定のユーザのモチベーションを推論する．modelがなければallのやつ使う
def predict(user="all"):
    print("<predict処理>")
    model=wether_to_np_net()
    model_dir="./model/"
    file_list=glob.glob("./model/*")
    # print(file_list)
    # txt読み込み
    user_list=open("./data_set/tokyo_user_list", "r").read().split("\n")
    user_list.pop(-1)#空白が入っているため
    if not(user in user_list) and user!="all":
        return -1
    # {"user_name":{day1:[chat_list],day2:[chat_list]}}
    if model_dir+user+".npz" in file_list:
        serializers.load_npz(model_dir+user+".npz", model)
    else:
        serializers.load_npz("./model/all.npz", model)
    optimizer = optimizers.Adam()
    optimizer.setup(model)

    # 入力データ読み込み#----
    f = open('./weather_info.json', 'r')
    input_data_json = json.load(f)#list
    f.close()
    print("データの日付"+str(input_data_json["dt"]))
    print("実際の日付"+str(datetime.date.today().strftime("%Y/%m/%d")))
    if input_data_json["dt"] != datetime.date.today().strftime("%Y/%m/%d"):
        weather_info.weather_info()
        f = open('./weather_info.json', 'r')
        input_data_json = json.load(f)#list
        f.close()
        print("変更")

    input_data=list(input_data_json.values())
    #日付以外
    #print(input_data)
    input_data=input_data[1:]
    #print(input_data)
    # 入力データ正規化
    input_data=normalization_input_data(input_data)
    # print(input_data)
    input_data=np.array([input_data],dtype=np.float32)

    res=model.forward(input_data)
    res=res[0][0]
    print("<res>")
    print(res)
    return res

if __name__ == "__main__":
    # tes
    print(predict(""))
