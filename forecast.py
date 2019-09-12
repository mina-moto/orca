import requests
import json
import datetime
import jpholiday
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

print(toHoliday(datetime.datetime.now()))
print(fromHoliday(datetime.datetime.now()))

city_id="1850147"
api_key=""
time_zone="Asia/Tokyo"

url="http://api.openweathermap.org/data/2.5/forecast/daily?id="+city_id+"&units=metric&cnt=3&appid="+api_key
url2="http://api.openweathermap.org/data/2.5/weather?id="+city_id+"&units=metric&appid="+api_key
response = requests.get(url)
response2 = requests.get(url2)
res=response.json()
res2=response.json()
print(res)
print(json.dumps(res, sort_keys = True, indent = 4))
print(len(res['list']))
data={'city':{'name':'Tokyo'},'cnt':res['cnt']+1,'list':[]}
c={'dt':timezone(time_zone).localize(timezone('UTC').localize(datetime.datetime.fromtimestamp(res2['dt'])))}
if res2['weather']['icon']=="01d" or res2['weather']['icon']=="02d" or res2['weather']['icon']=="03d" or res2['weather']['icon']=="04d":#crowd~clear
    c['weather_score']=(100.-c['clouds']['all'])/100
elif res2['weather']['icon']=="50d":#mist
    c['weather_score']=0
elif res2['weather']['icon']=="":#thunderstorm
    c['weather_score']=1
else :
    c['weather_score']=-0.95

c['temp_min']=res2['main']['temp_min']
c['temp_max']=res2['main']['temp_max']
c['temp_diff']=c['temp_max']-c['temp_min']
c['humidity']=res2['main']['pressure']
c['pressure']=res2['main']['humidity']
c['speed']=res2['wind']['speed']
c['to_holiday']=toHoliday(c['dt'])
c['from_holiday']=fromHoliday(c['dt'])
print(c['dt'])
data['list'].append(c)
for dic in res['list']:
    c={'dt':timezone(time_zone).localize(timezone('UTC').localize(datetime.datetime.fromtimestamp(dic['dt'])))}
    if dic['weather']['icon']=="01d" or dic['weather']['icon']=="02d" or dic['weather']['icon']=="03d" or dic['weather']['icon']=="04d":#crowd~clear
        c['weather_score']=(100.-c['clouds']['all'])/100
    elif dic['weather']['icon']=="50d":#mist
        c['weather_score']=0
    elif dic['weather']['icon']=="":#thunderstorm
        c['weather_score']=1
    else :
        c['weather_score']=-0.95

    c['temp_min']=dic['temp']['min']
    c['temp_max']=dic['temp']['max']
    c['temp_diff']=c['temp_max']-c['temp_min']
    c['humidity']=dic['pressure']
    c['pressure']=dic['humidity']
    c['speed']=dic['speed']
    c['to_holiday']=toHoliday(c['dt'])
    c['from_holiday']=fromHoliday(c['dt'])
    data['list'].append(c)
    print(c['dt'])

with open('forecast.json', 'w') as f:
    json.dump(data, f, indent=4)
