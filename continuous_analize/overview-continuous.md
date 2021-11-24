# window
- 「scan(解析対象になるファイルの一覧を検索)」「run」の２つのボタンを用意
- 「scan」の結果表示の場所(解析対象の一覧/不正なファイル配置(2つのデータが置かれていない時の警告))
- 解析対象となるディレクトリの名前(data-YYYYMMDDhhmm)の表示
- 「progress: n/N」みたいな表示
- 解析終了時にポップアップ

# 入出力
## 入力
指定のディレクトリ(プログラムと同じ階層の"data-YYYYMMDDhhmm"ディレクトリ)に, データのペア毎に入れるディレクトリをユーザーが作る

```examle
data
├── sample1
│   ├── Sample1_left.csv
│   └── Sample1_right.csv
├── sample2
│  ├── Sample2_left.csv
│  └── Sample2_right.csv
・
・
・
```
## 出力
- 解析したファイルのディレクトリに, 左右, Spectral Amplitude/Spectrogram, Sensor3つ, の計2\*2\*3=12枚の画像を出力
- 画像には, 単一ファイルの解析と同じように, グラフ4つ, 各種計算結果の値
- 値をまとめたcsvを書き出す

# 使い方
1. プログラム起動
1. 生成されたディレクトリ(data-YYYYMMDDhhmm)にファイルを用意
1. 「scan」で解析対象を確認
1. エラーがあればそれを解決, なければ「run」
1. 放置
1. ポップアップが出たら結果を確認