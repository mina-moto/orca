#東京の気象データ

import json
import csv
import datetime
import jpholiday
import collections as cl
from pytz import timezone
import numpy as np

#正規化
def zscore(x, axis = None):
    xmean = x.mean(axis=axis, keepdims=True)
    xstd  = np.std(x, axis=axis, keepdims=True)
    zscore = (x-xmean)/xstd
    return zscore

#関数（たけさん作）
def isBizDay(DATE):
    if DATE.weekday() >= 5 or jpholiday.is_holiday(DATE):
        return 0
    else:
        return 1

def toHoliday(d1):#d1:datetime
    cnt=0
    while isBizDay(d1.date())==1:
        d1+=datetime.timedelta(days=1)
        cnt+=1
    return cnt

def fromHoliday(d1):#d1:datetime
    cnt=0
    while isBizDay(d1.date())==1:
        d1-=datetime.timedelta(days=1)
        cnt+=1
    return cnt

#インポートしたCSVファイルの中身を辞書型にして入れるリスト
json_list = []
#keyの設定
keys = ('Y','m','d','temp_max','temp_min','humidity','Weather_score','speed','pressure') # 列数と要素数を一致させる

# CSV ファイルの読み込み
with open('./KisyotyoData/data.csv', 'r') as f:
    rowcount = 0
    for row in csv.DictReader(f, keys):
        rowcount = rowcount + 1
        #もし、データがなかったときに回避

        if rowcount < 6:
            continue

        #datetime型に変更
        if len(row['Y']) == 1:
            row['Y'] = '0' + row['Y']
        else:
            pass

        if len(row['m']) == 1:
            row['m'] = '0' + row['m']
        else:
            pass

        if len(row['d']) == 1:
            row['d'] = '0' + row['d']
        else:
            pass

        row['day'] = row['Y'] +'-'+ row['m'] +'-'+ row['d']

        del row['Y'],row['m'],row['d']
        day = row['day']
        dt = datetime.datetime.strptime(day, '%Y-%m-%d')

        #temp_diff（差分）の追加
        row['temp_diff'] = float(row['temp_max']) - float(row['temp_min'])
        #wscore
        wscore = 0
        wsum = 0
        for wsword in row['Weather_score']:
            if '晴' in wsword:
                wscore = wscore + 1
                wsum = wsum + 1;
            elif '曇' in wsword:
                wsum = wsum + 1;
            elif '雨' in wsword:
                wscore = wscore - 1
                wsum = wsum + 1;
            elif '雪' in wsword:
                wscore = wscore - 1
                wsum = wsum + 1;
            elif 'みぞれ' in wsword:
                wscore = wscore - 1
                wsum = wsum + 1;
            elif '雷' in wsword:
                wscore = wscore - 1
                wsum = wsum + 1;
            else:
                pass
        wscore = wscore / wsum
        row['Weather_score'] = wscore

        #休日からの日数
        row['to-holiday'] = toHoliday(dt)
        row['from-holiday'] = fromHoliday(dt)

        #rowをjson_listへ
        json_list.append(row)

        #cityの属性を追加
        weather_data = cl.OrderedDict()
        weather_data['list'] = json_list
        weather_data['city'] = {'name':'Tokyo'}

SekikaKeys = ('day','temp_max','temp_min','temp_diff','humidity','Weather_score','speed','pressure','to-holiday','from-holiday') # 列数と要素数を一致させる
SekikaMax = {}
SekikaMin = {}
SekikaSum = {}
SekikaAve = {}

weather_dataSekika = cl.OrderedDict()
json_seikika = []
floatDic = {}
linecount = 0

rowall = len(weather_data['list'])
#print(rowall)

#keyの数だけ回す
#'''
max_list = []
min_list = []
for Skey in SekikaKeys:

    SekikaMax[Skey] = -100000
    SekikaMin[Skey] =  100000
    SekikaSum[Skey] = 0
    SekikaAve[Skey] = 0
    #行の分だけ回す
    #最大、最小、平均算出

    #'day'以外をfloat化
    for maxmin in range(rowall):
        if Skey is not 'day' and Skey is not 'Weather_score' and Skey is not "to-holiday" and  Skey is not "from-holiday"and  Skey is not "temp_diff":
            welen = len(weather_data['list'][maxmin][Skey])
        else:
            welen = 1
        if welen is not 0 and Skey is not 'day':
            #print(weather_data['list'][maxmin][Skey])
            weather_data['list'][maxmin][Skey] = float(weather_data['list'][maxmin][Skey])
        elif Skey is 'day':
            continue
        else:
            weather_data['list'][maxmin][Skey] = -100

        #最大最小平均を得る
        if Skey == SekikaKeys[linecount]:
            if not weather_data['list'][maxmin][Skey] == -100:
            #print('OK')
                SekikaSum[Skey] = SekikaSum[Skey] + weather_data['list'][maxmin][Skey]
                if SekikaMax[Skey] < weather_data['list'][maxmin][Skey]:
                    SekikaMax[Skey] = weather_data['list'][maxmin][Skey]
                elif SekikaMin[Skey] > weather_data['list'][maxmin][Skey]:
                    SekikaMin[Skey] = weather_data['list'][maxmin][Skey]
                else:
                    pass
            else:
                pass
        else:
            pass

    SekikaAve[Skey] = SekikaSum[Skey] / rowall

    if weather_data['list'][maxmin][Skey] == -100:
        weather_data['list'][maxmin][Skey] = SekikaAve[Skey]

    #正規化
    count = 0
    for Sekika in range(rowall):
        if Skey is not 'day':
            if Skey == SekikaKeys[linecount]:
                count = count + 1
                weather_data['list'][Sekika][Skey] = (weather_data['list'][Sekika][Skey]-SekikaMin[Skey])/(SekikaMax[Skey]-SekikaMin[Skey])
        else:
            continue
    linecount = linecount + 1

max_list.append(SekikaMax)
min_list.append(SekikaMin)
maxmin_Dic = cl.OrderedDict()
maxmin_Dic['max'] = max_list
maxmin_Dic['min'] = min_list
maxmin_Dic['city'] = {'name':'Tokyo'}
#正規化した値の JSON ファイルへの書き込み
with open('output.json', 'w') as f:
    json.dump(weather_data, f,indent=4,ensure_ascii=False)
    json.dumps(weather_data,indent=4)

#最大値,最小値の JSON ファイルへの書き込み
with open('outputMaxMin.json', 'w') as f:
    json.dump(maxmin_Dic, f,indent=4,ensure_ascii=False)
    json.dumps(weather_dataSekika,indent=4)
# JSONファイルのロード
with open('output.json', 'r') as f:
    json_output = json.load(f)

print("{}".format(json.dumps(json_output,indent=4)))
