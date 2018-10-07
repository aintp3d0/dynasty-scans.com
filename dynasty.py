#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# __author__ = 'kira@-築城院 真鍳'

from os import remove, getcwd #--------#
from sys import argv, path #-----------#
from os.path import exists, dirname #--#
from requests import Session #---------#

# https://github.com/hhiki/funcs
path.append(dirname(getcwd()))
from funcs.chunks import get_proxy, mkd #---#


BASE = "https://dynasty-scans.com"
SESS = Session()
SESS.proxies = get_proxy(BASE)

def get_soup(url):
    return bs(SESS.get(url).text, 'lxml')


from PIL import Image #----------------#
from bs4 import BeautifulSoup as bs #--#
from img2pdf import convert #----------#
from argparse import ArgumentParser #--#
from collections import Counter #------#
from urllib.request import urlretrieve #
from multiprocessing import Pool #-----#


class DynastyScan:

    def __init__(self):
        self.base = 'https://dynasty-scans.com'
        self.down_url = []
        self.manga_pic = {}
        self.got_urllib = False
        self.manga_chapters = []
        self.m = None
        self.c = None
        self.s = None
        self.r = None


    def _rname(self, tar):
        """
        ignore list: [_Fly_by_Yuri.jpg, _Warning.png, _lil...]
        ADS startswith '_' = underscore, but I'm not sure
        """
        _rs = tar.split('/')
        st = _rs[-1].startswith('_')

        if not st and 'Fly_by_Yuri' not in _rs[-1]:
            return f"{_rs[-2]}_{_rs[-1].replace('%20', '_')}", True
        else:
            return False, False


    def get_manga_chapters(self, url):
        mkd(url.split('/')[-1])
        soup = get_soup(url)
        dd = soup.find('dl', 'chapter-list')

        for i in dd.find_all('a'):
            link = i.get('href')
            if link.startswith('/chapters/'):
                self.get_manga_pages("{}{}".format(self.base, link))


    def get_manga_pages(self, url):
        ke = url.split('/')[-1]

        if self.c and '#' in url:
            url = url.split('#')[0]

        self.get_image_url(url, ke)


    def _resize_images(self, fm):
        """ Resize pics with more used parametrs (width and height)
        """
        pics = [] # [((1400, 2000), 4), ((1398, 2000), 2), ((1404, 2000), 1)]

        for i in fm:
            img = Image.open(i)
            wid, hei = img.size
            pics.append((wid, hei)) 

        most = Counter(pics).most_common(1) # [((1400, 2000), 4)]
        width =  most[0][0][0] # 1400
        height = most[0][0][1] # 2000
        pics.clear()

        for i in fm:
            img = Image.open(i)
            nsize = img.resize((width, height))
            nsize.save(i)


    def _convert(self):
        """
        E:      if pics from self.manga_pic not exists in folder
        EType:  a bytes-like object is required, not 'str'

        EFIX::  not ignore exists pdf_
        """
        for k in self.manga_pic.keys():
            pdf_ = "{}.pdf".format(k)

            if not exists(pdf_):
                with open(pdf_, 'wb') as file:
                    try:
                        if self.r:
                            fm = [h for h in self.manga_pic[k]]
                            self._resize_images(fm)
                        file.write(convert([i for i in self.manga_pic[k]]))
                    except OSError:
                        print("Some pic have 0 bytes: remove pics and try again")
            # we can't ignore exists pdf_, but we need to delete all pics
            for i in self.manga_pic[k]:
                remove(i)


    def get_image_url(self, url, ke):
        """ Parse all urls and gen name for urls, save it before download urls

        ARCH :: dict = {'chapter1': ['pic1', 'pic2'...],
                        'chapter2': ['pic1', 'pic2'...]}

        E:      all pics will be in one Folder, here can be dublicates, and urlretrieve rewrites it
        EExm :: chapter1.pic1 = 0001.png;
                chapter2.pic1 = 0001.png;
        EFix :: gen name to pics with chapter-name
                chapter1_pic1.png
                chapter2_pic1.png
        """
        soup = get_soup(url)
        k = soup.find_all('script')[1]
        f = str(k).split('var pages = ')[1].split(';')[0].split(',')

        for i in f[::2]:
            r = i.replace('{"image":"', '').replace('"', '').replace('[', '')
            self.down_url.append(self.base+r)
            n0, n1 = self._rname(r)
            if n1:
                try:
                    if len(self.manga_pic[ke]) > 0: self.manga_pic[ke].append(n0)
                except KeyError:
                    self.manga_pic[ke] = [n0]

        self.mid_f()


    def mid_f(self):
        # http://toly.github.io/blog/2014/02/13/parallelism-in-one-line/
        pool = Pool()
        pool.map(self.download, self.down_url)
        pool.close()
        pool.join()


    def download(self, url):
        """
        EFIX::  nah rewrite exists pics

        EEXM::  OSError: image file is truncated (0 bytes not processed)
        EFIX::  remove pic which got Connection Error, but write bytes
        """
        n0, n1 = self._rname(url)

        if n1:
            if not exists(n0):
                try:
                    urlretrieve(url, n0)
                    if self.s: print(f'+ {url}')
                except urllib.error.URLError:
                    if exists(n0): remove(n0)
                    print('Bad internet connection: Try again!')
                    exit(1)


    def _arguments(self):
        """
        python3 dynasty.py -m https://dynasty-scans.com/anthologies/master_and_me
        python3 dynasty.py -c https://dynasty-scans.com/chapters/oneeloli_manga_123#12
        -s . ==  status, to make you sure that script nah dead
        """
        parser = ArgumentParser()
        parser.add_argument("-c", help="one chapter from manga")
        parser.add_argument("-m", help="manga with all chapters")
        parser.add_argument("-r", help="make 1 size for all images in pdf")
        parser.add_argument("-s", help="status: print info about downloaded pic")
        args = args = parser.parse_args()

        self.c = args.c
        self.m = args.m
        self.r = args.r
        self.s = args.s

        if args.c == args.m == args.r:
            print('python3 dynasty.py -h')


    def main(self):
        mkd('ManGa')

        if self.c:
            self.get_manga_pages(self.c)

        if self.m:
            self.get_manga_chapters(self.m)

        self._convert()


if __name__ == '__main__':
    yu = DynastyScan()
    yu._arguments()
    yu.main()
