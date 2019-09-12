#東京の気象データ

import json
import csv
import datetime
import jpholiday
import collections as cl
from pytz import timezone

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


json_list = []
keys = ('day','temp_max','temp_min','humidity','Weather_score','speed','pressure') # 列数と要素数を一致させる

# CSV ファイルの読み込み
with open('KisyoTokyo.csv', 'r') as f:
    for row in csv.DictReader(f, keys):
        #もし、データがなかったときに回避
        if row['temp_max'] is None:
            continue
        if row['temp_min'] is None:
            continue

        #datetime型に変更
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

        weather_data = cl.OrderedDict()
        weather_data['list'] = json_list
        weather_data['city'] = {'name':'Tokyo'}

# JSON ファイルへの書き込み
with open('output.json', 'w') as f:
    json.dump(weather_data, f,indent=4,ensure_ascii=False)
    json.dumps(weather_data,indent=4)

# JSONファイルのロード
with open('output.json', 'r') as f:
    json_output = json.load(f)
    print(type(json_output))

print("{}".format(json.dumps(json_output,indent=4)))
