import gremlin_call
import json
import codecs
import collections as cl
import datetime
import numpy as np
from collections import OrderedDict
import jpholiday
from pytz import timezone
import bisect


def isBizDay(DATE):
    if DATE.weekday() >= 5 or jpholiday.is_holiday(DATE):
        return 0
    else:
        return 1
#message_node取得
def get_user_reaction_nodes(user_name):
    query="g.V().hasLabel('user').has('fullName','"+user_name+"').out('adds')"
    node_list=gremlin_call.call_gremlin(query=query)
    return node_list

def count_work_day(begin,end):
    return (end-begin).days*5//7

def make_reaction_dataset():
    user_list=open("./data_set/tokyo_user_list", "r").read().split("\n")
    user_list.pop(-1)#空白が入っているため
    # {"user_name":{day1:[chat_list],day2:[chat_list]}}
    user_data=cl.OrderedDict()
    user_scr=cl.OrderedDict()
    user_min_max=cl.OrderedDict()
    user_data["all"]=cl.OrderedDict()
    user_scr["all"]=cl.OrderedDict()
    user_min_max["all"]=cl.OrderedDict()
    for user_name in user_list:
        user_data[user_name]=OrderedDict()
        user_scr[user_name]=OrderedDict()
        user_min_max[user_name]=OrderedDict()
        node_list=get_user_reaction_nodes(user_name)
        for node in node_list:
            length=len(node['properties']['name'])
            for i in range(length):
                dt=datetime.datetime.fromtimestamp(int(node['properties']['createdAt'][i]['value'])/1000).strftime("%Y/%m/%d")
                if dt in user_data[user_name]:
                    user_data[user_name][dt].append(node['properties']['name'][i]['value'])
                else :
                    user_data[user_name][dt]=[node['properties']['name'][i]['value']]
                if dt in user_data["all"]:
                    user_data["all"][dt].append(node['properties']['name'][i]['value'])
                else :
                    user_data["all"][dt]=[node['properties']['name'][i]['value']]
        print(user_name)
        if len(user_data[user_name])==0:
            cnt=0
        else:
            cnt=count_work_day(datetime.datetime.strptime(min(user_data[user_name].keys()), '%Y/%m/%d').date(),datetime.datetime.strptime(max(user_data[user_name].keys()), '%Y/%m/%d').date())
        print(cnt)
        eval=[2000000000]
        for dt in user_data[user_name]:
            eval.append(len(user_data[user_name][dt]))
        for i in range(max(cnt-len(eval),0)):
            eval.append(0)
        eval.sort()
        user_min_max[user_name]['zero_value']=(bisect.bisect_left(eval,0)+bisect.bisect_right(eval,0))/len(eval)/2
        for dt in user_data[user_name]:
            user_scr[user_name][dt]=(bisect.bisect_left(eval,len(user_data[user_name][dt]))+bisect.bisect_right(eval,len(user_data[user_name][dt])))/2/len(eval)#0~1にする

        #break#breakすると一人分
    if len(user_data["all"])==0:
        cnt=0
    else:
        cnt=count_work_day(datetime.datetime.strptime(min(user_data["all"].keys()), '%Y/%m/%d').date(),datetime.datetime.strptime(max(user_data["all"].keys()), '%Y/%m/%d').date())
    print(cnt)
    eval=[2000000000]
    for dt in user_data["all"]:
        eval.append(len(user_data["all"][dt]))
    for i in range(max(cnt-len(eval),0)):
        eval.append(0)
    eval.sort()
    user_min_max["all"]['zero_value']=(bisect.bisect_left(eval,0)+bisect.bisect_right(eval,0))/len(eval)/2
    for dt in user_data["all"]:
        user_scr["all"][dt]=(bisect.bisect_left(eval,len(user_data["all"][dt]))+bisect.bisect_right(eval,len(user_data["all"][dt])))/2/len(eval)#0~1にする
    f = codecs.open("reaction_dataset.json", "w", "utf-8")
    json.dump(user_data, f, indent=2, sort_keys=True, ensure_ascii=False)
    f.close()
    f = codecs.open("reaction_scr.json", "w", "utf-8")
    json.dump(user_scr ,f, indent=2, sort_keys=True, ensure_ascii=False)
    f.close()
    f = codecs.open("reaction_scr_zero_value.json", "w", "utf-8")
    json.dump(user_min_max ,f, indent=2, sort_keys=True, ensure_ascii=False)
    f.close()
        
    


make_reaction_dataset()
