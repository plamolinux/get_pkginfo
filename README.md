Script to check and download the updated package

## Usage

```
usage: get_pkginfo.py [-h] [-v] [-u URL] [-d | -s] [-o DOWNTODIR]
                      [-c CATEGORY] [-b] [-l LOCALBLOCK] [-a | -i] [-r]

Plamo Linux update packages check and download

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         verbose messages (not implemented yet)
  -u URL, --url URL     set URL to download
  -d, --download        download package(s)
  -s, --dlsubdir        download package(s) with subdir(s)
  -o DOWNTODIR, --downtodir DOWNTODIR
                        directory to save package(s)
  -c CATEGORY, --category CATEGORY
                        set category(s) to check
  -b, --blocklist       ignore block list
  -l LOCALBLOCK, --localblock LOCALBLOCK
                        set pkgname(s) to block
  -a, --autoinstall     install downloaded package(s) automatically
  -i, --interactive     install downloaded package(s) interactively
  -r, --reverse         find un-installed package(s)
```

```
○get_pkginfo コマンドの設定ファイル

/etc/pkginfo.conf : システムレベルで常に設定したい項目を指定する．
~/.pkginfo        : 個人レベルで設定したい項目を指定する．

/etc/pkginfo.conf，~/.pkginfoの順に設定ファイルを読み込み．指定した項目
は後者が優先される．

[検討事項]

デフォルトの設定値はスクリプト内に埋めこんでいるので，これらのファイル
は無くても動く．
常に指定したい項目は引数ではなく設定ファイルに書ける方が便利だけど，最
近のように非マルチユーザな使い方では，どちらかだけで十分な気がする．

○設定項目

URL        : チェック/ダウンロード先の URL
             (ex: ftp://plamo.linet.gr.jp/pub/Plamo-5.x/)．
DOWNTODIR  : ダウンロードしたパッケージの置き場所(要書き込みパーミッシ
             ョン)(ex: /var/Newpkgs)．
CATEGORY   : インストールしたカテゴリに関わらずチェックしたいカテゴリを
             指定する．
LOCALBLOCK : ブロックしたいパッケージ名．一行にベース名をスペース区切り
             で連ねて書く(ex: man man_db ffmpeg mplayer)．
INSTALL    : 自動インストールのモードを auto か manual にする．manual
             の場合，各パッケージのインストール前に確認する．auto の場
             合は問い合わせずにインストールを進める．

以下の項目は True/False で指定．
VERBOSE   : (未実装)
DOWNLOAD  : ダウンロードの有無．
DLSUBDIR  : ダウンロードしたパッケージをカテゴリごとのサブディレクトリに
            収めるか．
BLOCKLIST : ブロックリスト機能の有無．
REVERSE   : ローカルにインストールされていないパッケージを表示する．

○設定ファイル例

ex1:
URL = ftp://plamo.linet.gr.jp/pub/Plamo-5.x/
DOWNLOAD = False
DLSUBDIR = True
DOWNTODIR = /var/Newpkgs
CATEGORY = ''
BLOCKLIST = True
LOCALBLOCK = man man_db ffmpeg
INSTALL = ''
REVERSE = False

ex2:
CATEGORY = 00_base 03_xclassics 05_ext
LOCALBLOCK = 'man man_db ffmpeg'
INSTALL = manual

設定ファイルのパースは

if l.find("#") != 0:
    try:
        (d1, d2) = l.strip().split("=")
        key = d1.strip("' ")
        data = d2.strip("' ")
        confs[key] = data
    except ValueError:
        pass

くらいしかしてないので，行頭に "#" があればコメントとして無視，"=" で区
切られた2つの項目を key と data として読み込むので，data 部はクォートし
なくても複数の項目を書ける(' も strip はするのでクォートしてもいい)．

指定しなかった項目は，スクリプトに埋めこんだ以下のデフォルト値が使われ
る．

VERBOSE    : False (未実装)
URL        : ftp://ring.yamanashi.ac.jp/pub/linux/Plamo/Plamo-5.x/
DOWNLOAD   : False
DLSUBDIR   : False
DOWNTODIR  : '' (= cwd)
CATEGORY   : '' (無し)
BLOCKLIST  : True
LOCALBLOCK : '' (無し)
INSTALL    : '' (自動インストールしない)
REVERSE    : False

○引数による指定

これらの項目は引数によって指定，変更することもできる．指定可能な項目は
以下の通り．
-l (--localblock) 以外の設定は設定ファイルの値を上書きするので，設定フ
ァイルを変更せずに一時的に変更したい，という際に便利．

-v/--verbose     : 出力を冗長にする(未実装)．

-u/--url         : チェック/ダウンロード先の URL．
                   ftp://plamo.linet.gr.jp/pub/Plamo-5.x/ のように最後
                   の "/" まで必要．

-d/--download    : パッケージをダウンロードする(-s と排他)．

-s/--dlsubdir    : パッケージをサブディレクトリと共にダウンロードする
                   (-d と排他)．

-o/--downtodir   : パッケージをセーブする先のディレクトリを指定する．

-c/--category    : インストールしたカテゴリに関わらずチェックしたいカテ
                   ゴリを指定する．

-b/--blocklist   : ブロックリスト機能をオフにする(デフォルトオン)．

-l/--localblock  : ローカルにブロックしたいパッケージのベース名を指定す
                   る．
                   複数指定する場合は "man man_db ..." のようにスペース
                   で区切り，*クォートする*．
                   この項目は設定ファイルの指定に*追加される*．

-a/--autoinstall : 自動インストールモードを auto にする(-i と排他)．

-i/--interactive : 自動インストールモードを manual にする(-a と排他)．

-r/--reverse     : ローカルにインストールされていないパッケージを表示す
                   る．
```
