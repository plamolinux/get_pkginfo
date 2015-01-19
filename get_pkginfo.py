#!/usr/bin/python2
# -*- coding: euc-jp -*-

import argparse, subprocess, os, pickle, urllib2
import ftplib, datetime, time, sys

PKG_PATH = '/var/log/packages/'
#FTP_URL = 'ftp://plamo.linet.gr.jp/pub/Plamo-5.x/'
FTP_URL = 'ftp://ring.yamanashi.ac.jp/pub/linux/Plamo/Plamo-5.x/'
#FTP_URL = 'ftp://ftp.ring.gr.jp/pub/linux/Plamo/Plamo-5.x/'

def get_args():
    parser = argparse.ArgumentParser(description =
            'Plamo Linux update packages check and download')
    parser.add_argument('-d', '--download',
            action = 'store_true', help = 'download package(s)')
    parser.add_argument('-b', '--blocklist',
            action = 'store_true', help = 'ignore block list')
    parser.add_argument('-l', '--localblock',
            help = 'set local blocklist filename')
    args = parser.parse_args()
    return args

def get_arch():
    arch = subprocess.check_output('uname -m'.split()).strip()
    return 'x86' if arch == 'i686' else arch

def get_localpkgs():
    files = os.listdir(PKG_PATH)
    pkglist = {}
    for file in files:
        line = open(PKG_PATH + file, 'r').readline()
        (basename, vers, p_arch, build) = line[18:].strip().split("-")
        pkglist[basename] = (vers, p_arch, build)
    return pkglist

def get_ftp_pkgs(arch):
    url = FTP_URL + "allpkgs_" + arch + ".pickle"
    return pickle.load(urllib2.urlopen(url))

def download_pkg(hname, pname, fname):
    print("downloading: {}".format("ftp://" + hname + pname + "/" + fname))
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
        ftp.retrbinary("RETR %s" % fname, callback, blocksize = 1024)
    sys.stdout.write("\n")
    resp = ftp.sendcmd("MDTM %s" % fname)
    ftp.quit()
    dt = datetime.datetime.strptime(resp[4:18], "%Y%m%d%H%M%S")
    mtime = time.mktime((dt + datetime.timedelta(hours = 9)).timetuple())
    os.utime(fname, (mtime, mtime))

def rev_replaces(replaces):
    rev_list = {}
    for i in replaces.keys():
        new_pkgs = replaces[i][1]
        for j in new_pkgs:
            rev_list[j] = i
    return rev_list

def check_replaces(orig_list, replaces):
    replaced = []
    for ck in replaces.keys():
        if orig_list.has_key(ck):
            (ver, arch, build) = orig_list[ck]
            if replaces[ck][0] >= ver:
                del(orig_list[ck])
                for rep in replaces[ck][1]:
                    orig_list[rep] = (ver, arch, build)
                    replaced.append(rep)
    return orig_list, replaced

def get_localblock(blockfile):
    new_list = []
    with open(blockfile, 'r') as f:
        lbs = f.readlines()
    for i in lbs:
        if len(i.strip()) > 0:
            new_list.append(i.strip())
    return new_list

def main():
    param = get_args()
    '''
    my_arch: ���δĶ��� arch ̾(x86/x86_64)
    local_pkgs: ���δĶ��˥��󥹥ȡ���Ѥߥѥå������Υꥹ��
    ftp_pkgs: FTP�����о�ˤ���ѥå������Υꥹ��
    '''
    my_arch = get_arch()
    local_pkgs = get_localpkgs()
    ftp_pkgs = get_ftp_pkgs(my_arch)
    '''
    --localblock ���ץ����ǻ��ꤷ���ե����뤫�顤ɽ���оݳ��Ȥ���ե�
    ������ɤ߹��ߡ�blockpkgs ���ɲä��롥
    '''
    if param.localblock:
        if os.path.exists(param.localblock):
            new_block = []
            local_block = get_localblock(param.localblock)
            orig_block = ftp_pkgs['__blockpkgs']
            for i in orig_block:
                new_block.append(i)
            for i in local_block:
                new_block.append(i)
            ftp_pkgs['__blockpkgs'] = (new_block)
            #print("__blockpkgs:{}".format(ftp_pkgs['__blockpkgs']))
        else:
            print("localblock file: {} doesn't exist. "
                    "Ignore this option".format(param.localblock))
    '''
    -b ���ץ�������ꤷ�ʤ���С��֥�å��ꥹ�Ȥ˻��ꤷ���ѥå�����
    (ftp_pkgs['__blockpkgs'])��ɽ�����ʤ�(= local_pkgs �ꥹ�Ȥ������)
    '''
    if not param.blocklist:
        blocklist = ftp_pkgs['__blockpkgs']
        for bp in blocklist:
            del(local_pkgs[bp])
    '''
    ��̾��ʬ�䡤���󤷤��ѥå����������פ��������
    ftp_pkgs['__replaces'] �ˤϡ���������ѥå�������
    replace_list['old_name'] = (version, (new_name1, new_name2,,,))
    �Ȥ����������äƤ��ꡤcheck_replaces() �ǡ�local_pkgs['old_name'] ��
    local_pkgs['new_name1'] = (ver, arch, build) �η����Ȥ�ľ����
    ftp_pkgs['new_name1'] ����Ӥ��ƹ����оݤˤ��롥
    check_replaces() �Ǥϡ�local_pkgs[] �򸵤��Ȥ�ľ�����ꥹ��
    (check_pkgs[])�ȤɤΥѥå��������Ȥ�ľ�������ξ���(replaced[])���֤���
    ���κݡ�local_pkgs �� old_name �ϼ��ʤ���Τǡ�ɽ���Ѥ� rev_list
    �Ȥ��� 'new_name1' -> 'old_name', 'new_name2' -> 'old_name' �Τ褦
    �ʥǡ�����Ͽ���Ƥ�����replaced[] �ˤ���ѥå�����̾��ɽ������ݤ�
    �� rev_list[] ��Ȥ���
    '''
    replaces = ftp_pkgs['__replaces']
    rev_list = rev_replaces(replaces)
    (check_pkgs, replaced) = check_replaces(local_pkgs, replaces)
    for i in check_pkgs.keys():
        try:
            (ver, p_arch, build, ext, path) = ftp_pkgs[i]
            chk = (ver, p_arch, build)
            if check_pkgs[i] != chk:
                (local_ver, local_arch, local_build) = check_pkgs[i]
                if rev_list.has_key(i) and i in replaced:
                    print("** local package:{}-{}-{}-{} was renamed to".format(
                            rev_list[i], local_ver, local_arch, local_build))
                    print("** new package:{}-{}-{}-{}".format(
                            i, ver, p_arch, build))
                    print("** You should manually remove old package "
                            "(# removepkg {}) to update new one".format(
                            rev_list[i]))
                else:
                    print("local package:{}-{}-{}-{}".format(
                            i, local_ver, local_arch, local_build))
                    print("new package:{}-{}-{}-{}".format(
                            i, ver, p_arch, build))
                get_path = path.replace("/home/ftp/pub/Plamo-5.x/", "")
                url2 = FTP_URL + get_path + "/" + i + "-" + ver + "-" \
                        + p_arch + "-" + build + "." + ext
                print(url2)
                print("")
                if param.download:
                    hname = FTP_URL.split("/")[2]
                    pname = "/" + "/".join(FTP_URL.split("/")[3:-1]) \
                            + "/" + "/".join(get_path.split("/"))
                    fname = i + "-" + ver + "-" + p_arch + "-" \
                            + build + "." + ext
                    download_pkg(hname, pname, fname)
        except KeyError:
            sys.stderr.write(
                    "package: {} doesn't exist in FTP tree.\n".format(i))
            sys.stderr.write("\n")

if __name__ == "__main__":
    main()
