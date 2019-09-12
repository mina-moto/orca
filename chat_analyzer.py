import six
import json
import MeCab
import collections as cl #collectionsをインポート
from janome.tokenizer import Tokenizer
import codecs
from statistics import mean
from sklearn import preprocessing
import time
# pn_ja.dicファイルから，単語をキー，極性値を値とする辞書を得る
def load_pn_dict():
    dic = {}
    with codecs.open('./data_set/pn_ja.dic', 'r') as f:
        lines = f.readlines()
        for line in lines:
            # 各line="良い:よい:形容詞:0.999995"
            columns = line.split(':')
            dic[columns[0]] = float(columns[3])
    return dic

# トークンリストから極性値リストを得る('動詞','名詞', '形容詞', '副詞'のみ)
def get_pn_scores(tokens, pn_dic):
    scores = []
    for surface in [t.surface for t in tokens if t.part_of_speech.split(',')[0] in ['動詞', '名詞', '形容詞', '副詞']]:
        if surface in pn_dic:
            scores.append(pn_dic[surface])
    return scores

#引数文章のネガポジ計算
def calc_pn_score(doc,pn_dic):
    t = Tokenizer()
    tokens = t.tokenize(doc)
    pn_scores = get_pn_scores(tokens, pn_dic)
    if len(pn_scores)==0:
        return 0
    # print(pn_scores)
    return mean(pn_scores)

#引数の複数文章からネガポジ計算，辞書にあるトークンが30以下の場合Noneを返す
def calc_some_doc_pn_score(doc_list,pn_dic):
    tokens=generate_tokens(doc_list)
    if len(tokens)<=30:#速度改善
        return None
    pn_scores = get_pn_scores(tokens, pn_dic)
    if len(pn_scores)<=30:
        return None
    # print(len(pn_scores))
    return mean(pn_scores)

# 引数の複数文章から複数トークンtokensを生成
def generate_tokens(doc_list):
    tokens=[]
    t = Tokenizer()
    for doc in doc_list:
        tokens.extend(t.tokenize(doc))
    return tokens


#全ユーザの各日付のPN計算し保存，発言数が3以下とネガポジ辞書にある単語が30以下の日のデータは除く
def calc_all_pn_score():
    pn_dic=load_pn_dict()#ネガポジ辞書生成
    result_pn=cl.OrderedDict()
    with open('./chat_dataset.json') as f:
        chat_data = json.load(f)
    for user_name,user_data in chat_data.items():
        print(user_name)
        start=time.time()
        #user_nameのユーザの各日付のpn値
        user_pn=cl.OrderedDict()
        # 発言数が3以下の日のデータ削除
        user_data = {k: v for k, v in six.iteritems(user_data) if len(v) > 3}
        # print(len(user_data))
        # スコア計算
        score_list=[]
        score_day_list=[]#scoreのある日付
        for day,chat_list in user_data.items():
            # print(chat_list)
            score=calc_some_doc_pn_score(chat_list,pn_dic)
            if score!=None:
                score_day_list.append(day)
                score_list.append(score)
            # user_pn[day]=score
        if len(score_list)==0:
            continue
        # 0,1正規化
        score_list=preprocessing.minmax_scale(score_list)

        # 計算したスコアを保存
        for i,day in enumerate(score_day_list):
            user_pn[day]=score_list[i]
        result_pn[user_name]=user_pn

        t=time.time()-start#1ユーザかかった時間
        print("time:"+str(t)+"sec")


    w = open('./result/result_pn.json','w')
    json.dump(result_pn,w,indent=4,ensure_ascii=False)


if __name__ == "__main__":
    pn_score=calc_all_pn_score()
    # print(pn_score)
