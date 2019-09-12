import gremlin_call
import json
import codecs
import collections as cl
import datetime
from collections import OrderedDict

#message_node取得
def get_user_message_nodes(user_name):
    query="g.V().hasLabel('user').has('fullName','"+user_name+"').out('posts')"
    node_list=gremlin_call.call_gremlin(query=query)
    return node_list

def make_chat_dataset():
    user_list=open("./data_set/tokyo_user_list", "r").read().split("\n")
    user_list.pop(-1)#空白が入っているため
    # {"user_name":{day1:[chat_list],day2:[chat_list]}}
    user_data=cl.OrderedDict()
    user_data["all"]=cl.OrderedDict()
    for user_name in user_list:
        user_data[user_name]=OrderedDict()
        node_list=get_user_message_nodes(user_name)
        for node in node_list:
            length=len(node['properties']['text'])
            for i in range(length):
                dt=datetime.datetime.fromtimestamp(int(node['properties']['createdAt'][i]['value'])/1000).strftime("%Y/%m/%d")
                if dt in user_data[user_name]:
                    user_data[user_name][dt].append(node['properties']['text'][i]['value'])
                else :
                    user_data[user_name][dt]=[node['properties']['text'][i]['value']]
                if dt in user_data["all"]:
                    user_data["all"][dt].append(node['properties']['text'][i]['value'])
                else :
                    user_data["all"][dt]=[node['properties']['text'][i]['value']]
        #break#breakすると一人分
    f = codecs.open("chat_dataset.json", "w", "utf-8")
    json.dump(user_data, f, indent=2, sort_keys=True, ensure_ascii=False)
    f.close()


make_chat_dataset()
