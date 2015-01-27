#!/usr/bin/python2
# -*- coding: euc-jp -*-

import argparse, subprocess, os, pickle, urllib2
import ftplib, datetime, time, sys

PKG_PATH = "/var/log/packages/"
#FTP_URL = "ftp://plamo.linet.gr.jp/pub/Plamo-5.x/"
FTP_URL = "ftp://ring.yamanashi.ac.jp/pub/linux/Plamo/Plamo-5.x/"
#FTP_URL = "ftp://ftp.ring.gr.jp/pub/linux/Plamo/Plamo-5.x/"

def get_args():
    parser = argparse.ArgumentParser(description =
            "Plamo Linux update packages check and download")
    parser.add_argument("-d", "--download",
            action="store_true", help="download package(s)")
    parser.add_argument("-b", "--blocklist",
            action="store_true", help="ignore block list")
    parser.add_argument("-l", "--localblock",
            help="set local blocklist filename")
    args = parser.parse_args()
    return args

def get_arch():
    arch = subprocess.check_output("uname -m".split()).strip()
    return "x86" if arch == "i686" else arch

def get_local_pkgs():
    files = os.listdir(PKG_PATH)
    pkglist = {}
    for file in files:
        line = open(PKG_PATH + file, "r").readline()
        (basename, vers, p_arch, build) = line[18:].strip().split("-")
        pkglist[basename] = (vers, p_arch, build)
    return pkglist

def get_ftp_pkgs(arch):
    url = FTP_URL + "allpkgs_" + arch + ".pickle"
    return pickle.load(urllib2.urlopen(url))

def get_localblock(blockfile):
    new_list = []
    with open(blockfile, "r") as f:
        lbs = f.readlines()
    for i in lbs:
        if len(i.strip()) > 0:
            new_list.append(i.strip())
    return new_list

def rev_replaces(replaces):
    rev_list = {}
    for i in replaces.keys():
        rev_list[replaces[i]] = i
    return rev_list

def check_replaces(orig_list, replaces):
    for ck in replaces.keys():
        if ck in orig_list:
            (ver, arch, build) = orig_list[ck]
            del(orig_list[ck])
            orig_list[replaces[ck]] = (ver, arch, build)
    return orig_list

def download_pkg(url):
    hname = url.split("/")[2]
    pname = "/".join(url.split("/")[3:-1])
    fname = url.split("/")[-1]
    print("downloading: {}".format(fname))
    ftp = ftplib.FTP(hname)
    ftp.login()
    ftp.cwd(pname)
    count = [0]
    ftp.sendcmd("TYPE I")
    fsize = ftp.size(fname)
    sys.stdout.write("[ %10d / %10d ]" % (0, fsize))
    sys.stdout.flush()
    with open(fname, "w") as f:
        def callback(block):
            f.write(block)
            if count[0] < fsize:
                count[0] += 1024
            if count[0] > fsize:
                count[0] = fsize
            sys.stdout.write("\r[ %10d / %10d ]" % (count[0], fsize))
            sys.stdout.flush()
        ftp.retrbinary("RETR %s" % fname, callback, blocksize=1024)
    sys.stdout.write("\n")
    resp = ftp.sendcmd("MDTM %s" % fname)
    ftp.quit()
    dt = datetime.datetime.strptime(resp[4:18], "%Y%m%d%H%M%S")
    mtime = time.mktime((dt + datetime.timedelta(hours=9)).timetuple())
    os.utime(fname, (mtime, mtime))

def make_catlist(remote_pkgs):
    """
    00_base から 11_mate までの各カテゴリーに含まれるパッケージの
    basename を
    catlist["02_x11"] = ["IPAexfont", "IPAfont", "MesaLib", ...]
    のような辞書型のデータ catlist に収める処理
    """
    catlist = {}
    for i in remote_pkgs:
        if i != "__blockpkgs" and i != "__replaces":
            try:
                (ver, p_arch, build, ext, path) = remote_pkgs[i]
            except:
                print("remote key: {} have illegal data: {}"
                        .format(i, remote_pkgs[i]))
            dt = path.split("/")
            cat = dt[-2] if dt[-1].find(".txz") > 0 else dt[-1]
            tmp_list = catlist[cat] if cat in catlist else []
            tmp_list.append(i)
            catlist[cat] = tmp_list
    return catlist

def get_local_category(local_pkgs):
    """
    各カテゴリの代表的なパッケージのリスト．これらのパッケージがインス
    トール済みならば，そのカテゴリは選択されていたと考える．
    """
    local_category = ["00_base"]
    reps = {"01_minimum":"gcc",
            "02_x11":"xorg_server",
            "03_xclassics":"kterm",
            "04_xapps":"firefox",
            "05_ext":"mplayer",
            "06_xfce":"xfwm4",
            "07_kde":"kde_baseapps",
            "08_tex":"ptexlive",
            "09_kernel":"kernelsrc",
            "10_lof":"libreoffice_base",
            "11_mate":"mate_desktop"}
    for i in sorted(reps.keys()):
        if reps[i] in local_pkgs:
            local_category.append(i)
    return local_category

def main():
    param = get_args()
    """
    my_arch: この環境の arch 名(x86/x86_64)
    local_pkgs: この環境にインストール済みパッケージのリスト
    ftp_pkgs: FTPサーバ上にあるパッケージのリスト
    """
    my_arch = get_arch()
    local_pkgs = get_local_pkgs()
    ftp_pkgs = get_ftp_pkgs(my_arch)
    """
    --localblock オプションで指定したファイルから，表示対象外とするファ
    イルを読み込み，blockpkgs に追加する．
    """
    if param.localblock:
        if os.path.exists(param.localblock):
            new_block = []
            local_block = get_localblock(param.localblock)
            orig_block = ftp_pkgs["__blockpkgs"]
            for i in orig_block:
                new_block.append(i)
            for i in local_block:
                new_block.append(i)
            ftp_pkgs["__blockpkgs"] = (new_block)
        else:
            print("localblock file: {} doesn't exist.  "
                    "Ignore this option.".format(param.localblock))
    """
    -b オプションを指定しなければ，ブロックリストに指定したパッケージ
    (ftp_pkgs["__blockpkgs"])は表示しない(= local_pkgs リストから除く)
    """
    if not param.blocklist:
        blocklist = ftp_pkgs["__blockpkgs"]
        for bp in blocklist:
            del(ftp_pkgs[bp])
            del(local_pkgs[bp])
    """
    改名したパッケージを追跡するための処理．ftp_pkgs["__replaces"] には，
    該当するパッケージが replace_list["old_name"] = "new_name" という形
    で入っており，check_replaces() で，local_pkgs["old_name"] を
    local_pkgs["new_name"] = (ver, arch, build) の形に組み直し，
    ftp_pkgs["new_name"] と比較して更新対象にする．
    その際，local_pkgs の old_name は失なわれるので，表示用に
    replace_list[] を逆引きにした rev_list[] を使う．
    """
    replaces = ftp_pkgs["__replaces"]
    rev_list = rev_replaces(replaces)
    check_pkgs = check_replaces(local_pkgs, replaces)
    for i in sorted(check_pkgs.keys()):
        try:
            (ver, p_arch, build, ext, path) = ftp_pkgs[i]
            chk = (ver, p_arch, build)
            if check_pkgs[i] != chk:
                (local_ver, local_arch, local_build) = check_pkgs[i]
                if i in rev_list:
                    print("** local package: {}-{}-{}-{} was renamed to"
                            .format(rev_list[i], local_ver, local_arch,
                            local_build))
                    print("** new   package: {}-{}-{}-{}"
                            .format(i, ver, p_arch, build))
                    print("** You should manually remove old package "
                            "(# removepkg {}) to update new one."
                            .format(rev_list[i]))
                else:
                    print("local package: {}-{}-{}-{}"
                            .format(i, local_ver, local_arch, local_build))
                    print("new   package: {}-{}-{}-{}"
                            .format(i, ver, p_arch, build))
                url2 = "{}{}/{}-{}-{}-{}.{}".format(FTP_URL, path, i,
                        ver, p_arch, build, ext)
                print("URL: {}".format(url2))
                if param.download:
                    download_pkg(url2)
                print("")
        except KeyError:
            sys.stderr.write("package: {} doesn't exist in FTP tree.\n"
                    .format(i))
            sys.stderr.write("\n")
    """
    新しく追加されたパッケージをチェックする．cat_list{} は，FTP サーバ
    上にあるパッケージを，カテゴリをキーにして，そのカテゴリーに属する
    パッケージのリストを value に持った辞書型データ
    (cat_list["01_minimum"] =
            ["FDclone", "alsa_lib", "alsa_plugins", "alsa_utils", ...])
    intalled_category[] は，インストール時に選択したカテゴリのリスト．
    (["00_base", "01_minimum", "02_x11", "04_xapps", ...])
    installed_category[] に従って，cat_list{} にあるそのカテゴリのパッ
    ケージを調べ，ローカルにインストールされていないものがあれば表示す
    る．
    """
    cat_list = make_catlist(ftp_pkgs)
    installed_category = get_local_category(local_pkgs)
    for i in installed_category:
        for j in sorted(cat_list[i]):
            if j not in local_pkgs:
                (ver, p_arch, build, ext, path) = ftp_pkgs[j]
                pkgname = "{}-{}-{}-{}.{}".format(j, ver, p_arch, build, ext)
                print("** {} should be a new package in {} category."
                        .format(pkgname, i))
                url2 = "{}{}/{}".format(FTP_URL, path, pkgname)
                print("URL: {}".format(url2))
                if param.download:
                    download_pkg(url2)
                print("")

if __name__ == "__main__":
    main()
