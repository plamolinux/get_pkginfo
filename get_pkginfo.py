#! /usr/bin/python2

import sys, os, subprocess, pickle, argparse
from urllib2 import urlopen, URLError, HTTPError

PKG_PATH = '/var/log/packages/'
FTP_URL = 'ftp://plamo.linet.gr.jp/pub/Plamo-5.x/'

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
    parser = argparse.ArgumentParser(description='Plamo Linux update packages check and download')
    parser.add_argument('-d','--download', action='store_true', help='download package(s)')
    args = parser.parse_args()
    return args
        
def main():
    my_arch = get_arch()
    local_pkgs = get_localpkgs()
    ftp_pkgs = get_ftp_pkgs(my_arch)

    param = get_args()

    for i in local_pkgs.keys():
        try:
            (ver, p_arch, build, path) = ftp_pkgs[i]
            chk = (ver, p_arch, build)
            if local_pkgs[i] != chk:
                (local_ver, local_arch, local_build) = local_pkgs[i]
                print("local package:{}-{}-{}-{}".format(i, local_ver, local_arch, local_build))
                print("new package:{}-{}-{}-{}, path:{}".format(i, ver, p_arch, build, path))
                get_path = path.replace("/home/ftp/pub", "")
                url2 = "ftp://plamo.linet.gr.jp/pub/" + get_path + "/" + i + "-" + ver + "-" + p_arch + "-" + build + ".txz"
                print(url2)
                if param.download == True:
                    download_pkg(url2)
                print("")
        except KeyError:
            print("package: {} doesn't exit in FTP tree.".format(i))
            print("")

if __name__ == "__main__":
    main()
