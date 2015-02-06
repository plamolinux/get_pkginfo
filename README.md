Script to check and download the updated package

## Usage

```
usage: get_pkginfo.py [-h] [-d | -s] [-b] [-v] [-l LOCALBLOCK] [-r]
                      [-c CATEGORY] [-u URL] [-o OUTPUTDIR]

Plamo Linux update packages check and download

optional arguments:
  -h, --help            show this help message and exit
  -d, --download        download package(s)
  -s, --dlsubdir        download package(s) with subdir(s)
  -b, --blocklist       ignore block list
  -v, --verbose         verbose messages (not implemented yet)
  -l LOCALBLOCK, --localblock LOCALBLOCK
                        set pkgname(s) to block
  -r, --reverse         find un-installed package(s)
  -c CATEGORY, --category CATEGORY
                        set category(s) to check (not implemented yet)
  -u URL, --url URL     set URL to download
  -o OUTPUTDIR, --outputdir OUTPUTDIR
                        directory to save package(s)
```
