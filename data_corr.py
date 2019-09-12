#coding: UTF-8
# Numpy
import numpy as np
# Chainer
import chainer
import math
import random
import json
import time
import pandas

if __name__ == "__main__":
    # 入力データ読み込み
    f = open('./output.json', 'r')
    input_data_json = json.load(f)#list
    # print()
    f.close()
    # 天気の全入力データ
    input_data_list=[]
    for input in input_data_json["list"]:
        input=list(input.values())#ある日付の全値
        input_data_list.append(np.array(input))
        # input_data_list.append(input)
    #print(input_data_list)

    # 正解データ煮込み
    f = open('./result/result_pn.json', 'r')
    pn_json = json.load(f)
    user=""
    # あるユーザの日付ごとのネガポジ正解値
    input_data=[]
    tmp=pn_json[user].keys()
    tmp = list(map(lambda day: day.replace("/","-"), tmp))
    for input in input_data_list:
        if input[6] in tmp:
            #print(input[6])
            tmp_list=list(input)
            scr=pn_json[user][input[6].replace("-","/")]
            tmp_list[6]=tmp_list[6].replace("-","")
            tmp_list.append(min(tmp_list[9],tmp_list[8]))
            tmp_list.append(max(tmp_list[9],tmp_list[8]))
            tmp_list.append(int(tmp_list[6])%10000)
            tmp_list.append(int(tmp_list[6])%10000/100+int(tmp_list[6])%100)
            tmp_list.append(scr)
            #tmp_list=np.append(tmp_list,min(tmp_list[9],tmp_list[8]))
            #tmp_list=np.append(tmp_list,max(tmp_list[9],tmp_list[8]))
            #tmp_list=np.append(tmp_list,(pn_json[user][input[6].replace("-","/")]))
            #print(tmp_list)
            date=int(tmp_list[6])%10000
            m=4
            if date>m*100 and date<(m+3)*100:
                print(tmp_list[6])
                input_data.append(tmp_list)

    # モデルに入力するデータ
    input_data=np.array(input_data,dtype=np.float32)

    f.close()
    #print("****************************************************************************")
    np.set_printoptions(threshold=np.inf)
    #print(input_data)
    df = pandas.DataFrame(input_data)
    #print(df)
    print(len(df))
    df_corr = df.corr()
    print(df_corr)
    for input in input_data_json["list"]:
        print(input.keys())
        break


