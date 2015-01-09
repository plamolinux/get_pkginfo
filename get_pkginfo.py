#! /usr/bin/python2
# -*- coding: euc-jp -*-

import sys, os, subprocess, pickle, argparse
from urllib2 import urlopen, URLError, HTTPError

PKG_PATH = '/var/log/packages/'
# FTP_URL = 'ftp://plamo.linet.gr.jp/pub/Plamo-5.x/'
# FTP_URL = 'ftp://ftp.ring.gr.jp/pub/linux/Plamo/Plamo-5.x/'
FTP_URL = 'ftp://ring.yamanashi.ac.jp/pub/linux/Plamo/Plamo-5.x/'

def get_arch():
    res = subprocess.check_output(['uname', '-m'])
    if  res.strip() == 'x86_64':
        arch = 'x86_64'
    else:
        arch = 'x86'
    # print("arch:{}".format(arch))
    return(arch)

def get_localpkgs():
    files = os.listdir(PKG_PATH)
    pkglist = {}
    for file in files:
        file_path = PKG_PATH + file
        f = open(file_path, 'r')
        line = f.readline()
        (tmp, dt) = line.split(":")
        pkgname = dt.strip()
        # print(file, pkgname)
        (basename, vers, p_arch, build) = pkgname.split("-")
        pkglist[basename] = (vers, p_arch, build)

        # print(pkglist)
        # get pickled data
    return(pkglist)

def get_ftp_pkgs(arch):
    url = FTP_URL + "allpkgs_" + arch + ".pickle"
    response = urlopen(url)
    newpkgs = pickle.load(response)
    return(newpkgs)

def download_pkg(url):
    try:
        f = urlopen(url)
        print("downloading: {}".format(url))

        # Open our local file for writing
        with open(os.path.basename(url), "wb") as local_file:
            local_file.write(f.read())

    #handle errors
    except HTTPError, e:
        print "HTTP Error:", e.code, url
    except URLError, e:
        print "URL Error:", e.reason, url

def get_args():
    parser = argparse.ArgumentParser(description =
            'Plamo Linux update packages check and download')
    parser.add_argument('-d', '--download',
            action = 'store_true', help = 'download package(s)')
    parser.add_argument('-b', '--blocklist',
            action = 'store_true', help = 'ignore block list')
    args = parser.parse_args()
    return args

def check_replaces(orig_list, replaces):
    for ck in replaces.keys():
        # print(ck, replaces[ck][0])
        if orig_list.has_key(ck) == True :
            (ver, arch, build) = orig_list[ck]
            if replaces[ck][0] >= ver:
                del(orig_list[ck])
                for rep in replaces[ck][1]:
                    orig_list[rep] = (ver, arch, build)

    return(orig_list)

def rev_replaces(replaces):
    rev_list = {}
    for i in replaces.keys():
        new_pkgs = replaces[i][1]
        for j in new_pkgs:
            rev_list[j] = i

    return(rev_list)

def main():
    '''
    my_arch: ���δĶ��� arch ̾(x86/x86_64)
    local_pkgs: ���δĶ��˥��󥹥ȡ���Ѥߥѥå������Υꥹ��
    ftp_pkgs: FTP�����о�ˤ���ѥå������Υꥹ��
    '''
    my_arch = get_arch()
    local_pkgs = get_localpkgs()
    ftp_pkgs = get_ftp_pkgs(my_arch)

    param = get_args()

    '''
    -b ���ץ�������ꤷ�ʤ���С��֥�å��ꥹ�Ȥ˻��ꤷ���ѥå�����
    (ftp_pkgs['__blockpkgs'])��ɽ�����ʤ�(= local_pkgs �ꥹ�Ȥ������)
    '''
    if param.blocklist == False :
        blocklist = ftp_pkgs['__blockpkgs']
        for bp in blocklist:
            # print(bp)
            del(local_pkgs[bp])

    '''
    ��̾��ʬ�䡤���󤷤��ѥå����������פ��������
    ftp_pkgs['__replaces'] �ˤϡ���������ѥå�������
    replace_list['old_name'] = (version, (new_name1, new_name2,,,))
    �Ȥ����������äƤ��ꡤcheck_replaces() �ǡ�local_pkgs['old_name'] ��
    local_pkgs['new_name1'] = (ver, arch, build) �η����Ȥ�ľ����
    ftp_pkgs['new_name1'] ����Ӥ��ƹ����оݤˤ��롥
    ���κݡ�local_pkgs �� old_name �ϼ��ʤ���Τǡ�ɽ���Ѥ� rev_list
    �Ȥ��� 'new_name1' -> 'old_name', 'new_name2' -> 'old_name' �Τ褦
    �ʥǡ�����Ͽ���Ƥ�����
    '''
    replaces = ftp_pkgs['__replaces']
    rev_list = rev_replaces(replaces)
    check_pkgs = check_replaces(local_pkgs, replaces)

    for i in local_pkgs.keys():
        try:
            (ver, p_arch, build, ext, path) = ftp_pkgs[i]
            chk = (ver, p_arch, build)
            if local_pkgs[i] != chk:
                (local_ver, local_arch, local_build) = local_pkgs[i]
                if rev_list.has_key(i) == True :
                    pkgname = rev_list[i]
                else:
                    pkgname = i
                    print("local package:{}-{}-{}-{}".format(
                            pkgname, local_ver, local_arch, local_build))
                    print("new package:{}-{}-{}-{}".format(
                            i, ver, p_arch, build))
                    get_path = path.replace("/home/ftp/pub/Plamo-5.x/", "")
                    url2 = FTP_URL + get_path + "/" + i + "-" + ver + "-" \
                            + p_arch + "-" + build + "." + ext
                    print(url2)
                    print("")
                    if param.download == True:
                        download_pkg(url2)
        except KeyError:
            sys.stderr.write(
                    "package: {} doesn't exit in FTP tree.\n".format(i))
            sys.stderr.write("\n")

if __name__ == "__main__":
    main()
