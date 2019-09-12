import requests
import json
import datetime
import jpholiday
from pytz import timezone

def f2c(temp):
    return (temp-32)*5/9

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

def weather_info(api_key=""):
    city_name="tokyo,jp"
    time_zone="Asia/Tokyo"

    url="http://api.openweathermap.org/data/2.5/weather?q="+city_name+"&units=metric&appid="+api_key
    #print(url)
    response = requests.get(url)
    res=response.json()
    #print(res)
    #print(json.dumps(res, sort_keys = True, indent = 4))
    time=timezone(time_zone).localize((datetime.datetime.fromtimestamp(res['sys']['sunrise'])))
    c={
    'dt':time.strftime("%Y/%m/%d")
    ,'temp_max':res['main']['temp_max']
    ,'temp_min':res['main']['temp_min']
    ,'humidity':res['main']['humidity']
    ,'Weather_score':0
    ,'speed':res['wind']['speed']
    ,'pressure':res['main']['pressure']
    ,'temp_diff':0
    ,'to_holiday':toHoliday(time)
    ,'from_holiday':fromHoliday(time)
    }
    if res['weather'][0]['icon']=="01d" or res['weather'][0]['icon']=="02d" or res['weather'][0]['icon']=="03d" or res['weather'][0]['icon']=="04d":#crowd~clear
        c['Weather_score']=(100.-res['clouds']['all'])/100
    elif res['weather'][0]['icon']=="50d":#mist
        c['Weather_score']=0
    elif res['weather'][0]['icon']=="":#thunderstorm
        c['Weather_score']=1
    else :
        c['Weather_score']=-0.95
    c['temp_diff']=c['temp_max']-c['temp_min']

    with open('weather_info.json', 'w') as f:
        json.dump(c, f, indent=4)

if __name__ == '__main__':
    weather_info()