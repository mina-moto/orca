import json
import collections as cl #collectionsをインポート
if __name__ == "__main__":
    # チャットのネガポジ
    f = open('./result/result_pn.json', 'r')
    pn = json.load(f)
    pn_user_list=list(pn.keys())

    # reactionのデータ
    f = open('./reaction_scr.json', 'r')
    reaction_scr = json.load(f)

    # reactionのデータがないときに補完するデータ
    f = open('./reaction_scr_zero_value.json', 'r')
    reaction_scr_zero_value = json.load(f)
    f.close()

    #result_pn_reaction
    result_pn_reaction=cl.OrderedDict()

    for pn_user in pn_user_list:
        if not(pn_user in reaction_scr):
            print(pn_user)
            continue
        result_pn_reaction[pn_user]=cl.OrderedDict()
        for day,score in pn[pn_user].items():
            merge_score=0
            # reaction_scrにpnのdayがあれば
            if day in reaction_scr[pn_user]:
                merge_score=(score+reaction_scr[pn_user][day])/2
            else:# なければzero_valueを使う
                merge_score=(score+reaction_scr_zero_value[pn_user]["zero_value"])/2
            result_pn_reaction[pn_user][day]=merge_score
    # print(result_pn_reaction)
        # for day,score in day_data:
        #     if day in day_data:
    w = open('./result/result_pn_reaction.json','w')
    json.dump(result_pn_reaction,w,indent=4,ensure_ascii=False)

    # f = open('./result_pn_reaction.json', 'r')
    # result_pn_reaction = json.load(f)
    # user_list=list(pn_json.keys())
    # f.close()
