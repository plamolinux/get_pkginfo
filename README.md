Script to check and download the updated package

## Usage

```
usage: get_pkginfo.py [-h] [-v] [-u URL] [-d | -s] [-o DOWNTODIR]
                      [-c CHKCATEGORY] [-b] [-l LOCALBLOCK]

Plamo Linux update packages check and download

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         verbose messages (not implemented yet)
  -u URL, --url URL     set URL to download
  -d, --download        download package(s)
  -s, --dlsubdir        download package(s) with subdir(s)
  -o DOWNTODIR, --downtodir DOWNTODIR
                        directory to save package(s)
  -c CHKCATEGORY, --chkcategory CHKCATEGORY
                        set category(s) to check (not implemented yet)
  -b, --blocklist       ignore block list
  -l LOCALBLOCK, --localblock LOCALBLOCK
                        set pkgname(s) to block
```

```
��get_pkginfo ���ޥ�ɤ�����ե�����

/etc/pkginfo.conf : �����ƥ��٥�Ǿ�����ꤷ�������ܤ���ꤹ�롥
~/.pkginfo        : �Ŀͥ�٥�����ꤷ�������ܤ���ꤹ�롥

/etc/pkginfo.conf��~/.pkginfo�ν������ե�������ɤ߹��ߡ����ꤷ������
�ϸ�Ԥ�ͥ�褵��롥

[��Ƥ����]

�ǥե���Ȥ������ͤϥ�����ץ������ᤳ��Ǥ���Τǡ������Υե�����
��̵���Ƥ�ư����
��˻��ꤷ�������ܤϰ����ǤϤʤ�����ե�����˽񤱤��������������ɡ���
��Τ褦����ޥ���桼���ʻȤ����Ǥϡ��ɤ��餫�����ǽ�ʬ�ʵ������롥

���������

URL         : �����å�/������������ URL
              (ex: ftp://plamo.linet.gr.jp/pub/Plamo-5.x/)��
DOWNTODIR   : ��������ɤ����ѥå��������֤����(�׽񤭹��ߥѡ��ߥå�
              ���)(ex: /var/Newpkgs)��
CHKCATEGORY : ���󥹥ȡ��뤷�����ƥ���˴ؤ�餺�����å����������ƥ���
              ����ꤹ��(̤����)��
LOCALBLOCK  : �֥�å��������ѥå�����̾����Ԥ˥١���̾�򥹥ڡ�������
              ���Ϣ�ͤƽ�(ex: man man_db ffmpeg mplayer)��

�ʲ��ι��ܤ� True/False �ǻ��ꡥ
VERBOSE   : (̤����)
DOWNLOAD  : ��������ɤ�̵ͭ��
DLSUBDIR  : ��������ɤ����ѥå������򥫥ƥ��ꤴ�ȤΥ��֥ǥ��쥯�ȥ��
            ����뤫��
BLOCKLIST : �֥�å��ꥹ�ȵ�ǽ��̵ͭ��

������ե�������

ex1:
URL = ftp://plamo.linet.gr.jp/pub/Plamo-5.x/
DOWNLOAD = False
DLSUBDIR = True
DOWNTODIR = /var/Newpkgs
BLOCKLIST = True
LOCALBLOCK = man man_db ffmpeg

ex2:
LOCALBLOCK = 'man man_db ffmpeg'

����ե�����Υѡ�����

if l.find("#") != 0:
    try:
        (d1, d2) = l.strip().split("=")
        key = d1.strip("' ")
        data = d2.strip("' ")
        confs[key] = data
    except ValueError:
        pass

���餤�������Ƥʤ��Τǡ���Ƭ�� "#" ������Х����ȤȤ���̵�롤"=" �Ƕ�
�ڤ�줿2�Ĥι��ܤ� key �� data �Ȥ����ɤ߹���Τǡ�data ���ϥ������Ȥ�
�ʤ��Ƥ�ʣ���ι��ܤ�񤱤�(' �� strip �Ϥ���Τǥ������Ȥ��Ƥ⤤��)��

���ꤷ�ʤ��ä����ܤϡ�������ץȤ���ᤳ����ʲ��Υǥե�����ͤ��Ȥ��
�롥

VERBOSE      : False (̤����)
URL          : ftp://ring.yamanashi.ac.jp/pub/linux/Plamo/Plamo-5.x/
DOWNLOAD     : False
DLSUBDIR     : False
DOWNTODIR    : "" (= cwd)
CHKCATEGORY  : "" (̵��) (̤����)
BLOCKLIST    : True
LOCALBLOCK   : "" (̵��)

�������ˤ�����

�����ι��ܤϰ����ˤ�äƻ��ꡤ�ѹ����뤳�Ȥ�Ǥ��롥�����ǽ�ʹ��ܤ�
�ʲ����̤ꡥ
-l (--localblock) �ʳ������������ե�������ͤ��񤭤���Τǡ������
��������ѹ������˰��Ū���ѹ����������Ȥ����ݤ�������

-v/--verbose     : ���Ϥ��Ĺ�ˤ���(̤����)��

-u/--url         : �����å�/������������ URL��
                   ftp://plamo.linet.gr.jp/pub/Plamo-5.x/ �Τ褦�˺Ǹ�
                   �� "/" �ޤ�ɬ�ס�

-d/--download    : �ѥå��������������ɤ���(-s ����¾)��

-s/--dlsubdir    : �ѥå������򥵥֥ǥ��쥯�ȥ�ȶ��˥�������ɤ���
                   (-d ����¾)��

-o/--downtodir   : �ѥå������򥻡��֤�����Υǥ��쥯�ȥ����ꤹ�롥

-c/--chkcategory : ���󥹥ȡ��뤷�����ƥ���˴ؤ�餺�����å�����������
                   �������ꤹ��(̤����)��

-b/--blocklist   : �֥�å��ꥹ�ȵ�ǽ�򥪥դˤ��롥

-l/--localblock  : ������˥֥�å��������ѥå������Υ١���̾����ꤹ
                   �롥
                   ʣ�����ꤹ����� "man man_db ..." �Τ褦�˥��ڡ���
                   �Ƕ��ڤꡤ*�������Ȥ���*��
                   ���ι��ܤ�����ե�����λ����*�ɲä����*��
```
