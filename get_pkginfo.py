#!/usr/bin/python2
# -*- coding: euc-jp -*-

import argparse, subprocess, os, pickle, urllib2
import ftplib, sys, datetime, time

PKG_PATH = "/var/log/packages/"

def get_args():
    parser = argparse.ArgumentParser(description="Plamo Linux update "
            "packages check and download")
    parser.add_argument("-v", "--verbose", action="store_true",
            help="verbose messages (not implemented yet)")
    parser.add_argument("-u", "--url",
            help="set URL to download")
    mexgrp = parser.add_mutually_exclusive_group()
    mexgrp.add_argument("-d", "--download", action="store_true",
            help="download package(s)")
    mexgrp.add_argument("-s", "--dlsubdir", action="store_true",
            help="download package(s) with subdir(s)")
    parser.add_argument("-o", "--downtodir",
            help="directory to save package(s)")
    parser.add_argument("-c", "--chkcategory",
            help="set category(s) to check (not implemented yet)")
    parser.add_argument("-b", "--blocklist", action="store_false",
            help="ignore block list")
    parser.add_argument("-l", "--localblock",
            help="set pkgname(s) to block")
    parser.add_argument("-r", "--reverse", action="store_true",
            help="find un-installed package(s)")
    return parser.parse_args()

def get_system_confs():
    conf_file = "/etc/pkginfo.conf"
    confs = {}
    if os.path.isfile(conf_file):
        with open(conf_file, "r") as f:
            lines = f.readlines()
        for l in lines:
            if l.find("#") != 0:
                try:
                    (d1, d2) = l.strip().split("=")
                    key = d1.strip("' ")
                    data = d2.strip("' ")
                    if data == "True":
                      data = True
                    elif data == "False":
                      data = False
                    confs[key] = data
                except ValueError:
                    pass
    return confs

def get_local_confs():
    homedir = os.path.expanduser("~")
    conf_file = homedir + "/" + ".pkginfo"
    confs = {}
    if os.path.isfile(conf_file):
        with open(conf_file, "r") as f:
            lines = f.readlines()
        for l in lines:
            if l.find("#") != 0:
                try:
                    (d1, d2) = l.strip().split("=")
                    key = d1.strip("' ")
                    data = d2.strip("' ")
                    if data == "True":
                      data = True
                    elif data == "False":
                      data = False
                    confs[key] = data
                except ValueError:
                    pass
    return confs

def get_param_confs():
    confs = {}
    param = get_args()
    if param.verbose:
        confs["VERBOSE"] = True
    if param.url:
        confs["URL"] = param.url
    if param.download:
        confs["DOWNLOAD"] = True
    if param.dlsubdir:
        confs["DLSUBDIR"] = True
    if param.downtodir:
        confs["DOWNTODIR"] = param.downtodir
    if param.chkcategory:
        confs["CHKCATEGORY"] = param.chkcategory
    if not param.blocklist:
        confs["BLOCKLIST"] = False
    if param.localblock:
        confs["LOCALBLOCK"] = param.localblock
    if param.reverse:
        confs["REVERSE"] = True
    return confs

def get_confs():
    system_confs = get_system_confs()
    local_confs = get_local_confs()
    param_confs = get_param_confs()
    # defaults configs
    confs = {"VERBOSE": False,
            "URL": "ftp://ring.yamanashi.ac.jp/pub/linux/Plamo/Plamo-5.x/",
            "DOWNLOAD": False,
            "DLSUBDIR": False,
            "DOWNTODIR": "",
            "CHKCATEGORY": "",
            "BLOCKLIST": True,
            "REVERSE": False}
    """
    各種設定は，
    引数 --> ローカル(~/.pkginfo) --> システム(/etc/pkginfo.conf)
    の順に評価する．
    """
    for i in confs.keys():
        if i in param_confs:
            confs[i] = param_confs[i]
        elif i in local_confs:
            confs[i] = local_confs[i]
        elif i in system_confs:
            confs[i] = system_confs[i]

    """
    ローカルでブロックしたいパッケージは追加する方が便利だろう．
    """
    confs["LOCALBLOCK"] = ""
    try:
        system_confs["LOCALBLOCK"]
        confs["LOCALBLOCK"] = \
                confs["LOCALBLOCK"] + " " + system_confs["LOCALBLOCK"]
    except KeyError:
        pass
    try:
        local_confs["LOCALBLOCK"]
        confs["LOCALBLOCK"] = \
                confs["LOCALBLOCK"] + " " + local_confs["LOCALBLOCK"]
    except KeyError:
        pass
    try:
        param_confs["LOCALBLOCK"]
        confs["LOCALBLOCK"] = \
                confs["LOCALBLOCK"] + " " + param_confs["LOCALBLOCK"]
    except KeyError:
        pass
    return confs

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

def get_ftp_pkgs(arch, confs):
    url = confs["URL"] + "allpkgs_" + arch + ".pickle"
    return pickle.load(urllib2.urlopen(url))

def check_replaces(orig_list, replaces):
    for ck in replaces.keys():
        if ck in orig_list:
            (ver, arch, build) = orig_list[ck]
            del(orig_list[ck])
            orig_list[replaces[ck]] = (ver, arch, build)
    return orig_list

def rev_replaces(replaces):
    rev_list = {}
    for i in replaces.keys():
        rev_list[replaces[i]] = i
    return rev_list

def download_pkg(url, confs, subdir):
    hname = url.split("/")[2]
    pname = "/".join(url.split("/")[3:-1])
    fname = url.split("/")[-1]
    print("downloading: {}".format(fname))
    if confs["DOWNTODIR"]:
        if not os.path.isdir(confs["DOWNTODIR"]):
            os.makedirs(confs["DOWNTODIR"])
        cwd = os.getcwd()
        os.chdir(confs["DOWNTODIR"])
        if confs["DLSUBDIR"]:
            if not os.path.isdir(subdir):
                os.makedirs(subdir)
            os.chdir(subdir)
    elif confs["DLSUBDIR"]:
        if not os.path.isdir(subdir):
            os.makedirs(subdir)
        cwd = os.getcwd()
        os.chdir(subdir)
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
    try:
        os.chdir(cwd)
    except NameError:
        pass

def make_catlist(remote_pkgs):
    """
    00_base から 11_mate までの各カテゴリーに含まれるパッケージの
    basename を
    catlist["02_x11"] = ["IPAexfont", "IPAfont", "MesaLib", ...]
    のような辞書型のデータ catlist に収める処理
    """
    catlist = {}
    for i in remote_pkgs:
        if i not in ["__blockpkgs", "__replaces"]:
            try:
                (ver, p_arch, build, ext, path) = remote_pkgs[i]
            except:
                print("remote key: {} have illegal data: {}"
                        .format(i, remote_pkgs[i]))
            else:
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
    reps = {"01_minimum": "gcc",
            "02_x11": "xorg_server",
            "03_xclassics": "kterm",
            "04_xapps": "firefox",
            "05_ext": "mplayer",
            "06_xfce": "xfwm4",
            "07_kde": "kde_baseapps",
            "08_tex": "ptexlive",
            "09_kernel": "kernelsrc",
            "10_lof": "libreoffice_base",
            "11_mate": "mate_desktop"}
    for i in sorted(reps.keys()):
        if reps[i] in local_pkgs:
            local_category.append(i)
    return local_category

def main():
    confs = get_confs()
    """
    my_arch: この環境の arch 名(x86/x86_64)
    local_pkgs: この環境にインストール済みパッケージのリスト
    ftp_pkgs: FTPサーバ上にあるパッケージのリスト
    """
    my_arch = get_arch()
    local_pkgs = get_local_pkgs()
    ftp_pkgs = get_ftp_pkgs(my_arch, confs)
    """
    LOCALBLOCK (--localblock) オプションで指定したパッケージ名を，
    blockpkgs に追加する．
    """
    if confs["LOCALBLOCK"]:
        new_block = []
        for i in ftp_pkgs["__blockpkgs"]:
            new_block.append(i)
        for i in confs["LOCALBLOCK"].split():
            new_block.append(i)
        ftp_pkgs["__blockpkgs"] = new_block
    """
    -b オプションを指定しなければ，ブロックリストに指定したパッケージ
    (ftp_pkgs["__blockpkgs"])は表示しない(= local_pkgs リストから除く)
    """
    if confs["BLOCKLIST"] and not confs["REVERSE"]:
        for bp in ftp_pkgs["__blockpkgs"]:
            if bp in local_pkgs:
                del(local_pkgs[bp])
            if bp in ftp_pkgs:
                del(ftp_pkgs[bp])
    """
    改名したパッケージを追跡するための処理．ftp_pkgs["__replaces"] には，
    該当するパッケージが replace_list["old_name"] = "new_name" という形
    で入っており，check_replaces() で，local_pkgs["old_name"] を
    local_pkgs["new_name"] = (ver, arch, build) の形に組み直し，
    ftp_pkgs["new_name"] と比較して更新対象にする．
    その際，local_pkgs の old_name は失なわれるので，表示用に
    replace_list[] を逆引きにした rev_list[] を使う．
    """
    check_pkgs = check_replaces(local_pkgs, ftp_pkgs["__replaces"])
    rev_list = rev_replaces(ftp_pkgs["__replaces"])
    if confs["REVERSE"]:
        not_installed = []
        for i in ftp_pkgs.keys():
            if i in ["__blockpkgs", "__replaces"]:
                continue
            if not local_pkgs.has_key(i):
                (ver, p_arch, build, ext, path) = ftp_pkgs[i]
                pkgname = "{}-{}-{}-{}.{}".format(i, ver, p_arch, build, ext)
                path_list = "{}/{}".format(path, pkgname).split("/")[2:]
                not_installed.append((path_list, path, pkgname))
        print("un-selected packages:")
        """
        カテゴリー別に，カテゴリー内のパッケージを Plamo インストーラが
        インストールする順番にソートして表示する．
        """
        print("category: {}".format(sorted(not_installed)[0][0][0]))
        ct_prev = sorted(not_installed)[0][0][0]
        for i in sorted(not_installed):
            if i[0][0] != ct_prev:
                print("category: {}".format(i[0][0]))
            ct_prev = i[0][0]
            print("\t{}".format("/".join(i[0][1:])))
            if confs["DOWNLOAD"] or confs["DLSUBDIR"]:
                url2 = "{}{}/{}".format(FTP_URL, i[1], i[2])
                download_pkg(url2, confs, "/".join(i[0]))
        return
    for i in sorted(check_pkgs.keys()):
        try:
            (ver, p_arch, build, ext, path) = ftp_pkgs[i]
        except KeyError:
            sys.stderr.write("package: {} doesn't exist in FTP tree.\n\n"
                    .format(i))
        else:
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
                url2 = "{}{}/{}-{}-{}-{}.{}".format(confs["URL"], path, i,
                        ver, p_arch, build, ext)
                print("URL: {}".format(url2))
                if confs["DOWNLOAD"] or confs["DLSUBDIR"]:
                    download_pkg(url2, confs, "/".join(path.split("/")[2:]))
                print("")
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
                url2 = "{}{}/{}".format(confs["URL"], path, pkgname)
                print("URL: {}".format(url2))
                if confs["DOWNLOAD"] or confs["DLSUBDIR"]:
                    download_pkg(url2, confs, "/".join(path.split("/")[2:]))
                print("")

if __name__ == "__main__":
    main()
