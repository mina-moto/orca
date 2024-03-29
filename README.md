ORCA

## ネガポジ判定
- 手法：ユーザの各チャットデータの形態素解析を行い，ユーザごと各日付ごとに全単語のネガポジの平均を算出し0から1で正規化．
- 上記とは別に汎用的なものとして全ユーザの日付ごとの全単語のネガポジの平均．
- 極性値の辞書にはこちらを使用<http://www.lr.pi.titech.ac.jp/~takamura/pndic_ja.html>
### 前処理
- '動詞','名詞', '形容詞', '副詞'のみ扱う．
- 1日の発言が3回以下の日は除く
- 1日の全ての発言の合計単語数のうち辞書にあるものが30以下の日は除く

チャットデータダウンロードし保存
```
make_chat_dataset.py
```

チャットデータからネガポジ判定を行い保存
```
chat_analyzer.py
```

## 天候からネガポジ予測
- ニューラルネットワーク
- 入力は[天気,最低気温,最高気温,気温差分,湿度,気圧,風速,休日までの日数,休日からの日数]の9つを0から1に正規化したもの
- 出力は0から1のポジティブ度，正解ラベルはchat_analyzer.pyによるネガポジ判定結果．
- ユーザごとに学習しモデルを構築．
- ユーザを指定し，今日の天候からポジティブ度を予測する．
- データ数が100以下のユーザは全ユーザのデータで学習した汎用的なモデルを用いる．

全ユーザの学習
```
python wether_to_np_net.py
```

ユーザを指定し，今日の天候からポジティブ度を予測
```
python predict.py
```
