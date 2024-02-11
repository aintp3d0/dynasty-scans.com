#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# __author__ = 'ames0k0'

from bs4 import BeautifulSoup as bs
from sys import path
from json import load, dump
from os.path import exists, dirname
from requests import Session
from argparse import ArgumentParser

from utils import mkd


BASE_DIR = 'Updates'


class Check:
    """
    If status Manga is Ongoing, wanna know when you can read next chapter,
        and wondering how you can find this Manga...
    Just [a]dd url and [c]heck when you wanna read this Manga

    [d]el url when new chapters nah coming

    ::EXP:ADD:: a -> https://dynasty-scans.com/series/shouraiteki_ni_shindekure
    ::EXP:DEL:: d -> https://dynasty-scans.com/series/shouraiteki_ni_shindekure
    ::EXP:CHE:: c -> ==================================================
                      ! URL:  https://dynasty-scans.com/series/shouraiteki_ni_shindekure
                      + UPD:  https://dynasty-scans.com/chapters/shouraiteki_ni_shindekure_ch03
                      + UPD:  https://dynasty-scans.com/chapters/shouraiteki_ni_shindekure_ch04
                     ==================================================
    """
    def __init__(self, proxy):
        self.file = f"{BASE_DIR}/manga.json"
        self.base = "https://dynasty-scans.com"
        self.sess = Session()
        if proxy:
            self.sess.proxies = proxy

    def _ld(self):
        try:
            with open(self.file, 'r') as f: return load(f)
        except Exception as e:
            print('\nERR:: NO URL YET\n')
            exit(0)

    def _dmd(self, data):
        with open(self.file, 'w') as f: dump(data, f)

    def _get_soup(self, url):
        r = self.sess.get(url)
        return bs(r, 'lxml')

    def gen_json(self):
        """
                + chapter_1
        url --> + chapter_2 --> {url: [chapter_1, chapter_2, chapter_3]}
                + chapter_3
        """
        url = input('URL: ')
        if url.startswith(self.base):
            chapters = []
            soup = self._get_soup(url)
            manga = soup.find('dl', "chapter-list")
            for chapter in manga.find_all('a', 'name'):
                urls = self.base + chapter.get('href')
                print(f' + CHP: {urls}')
                chapters.append(urls)
            data = {url:chapters}
            self.dm(data, None)
        else: print('Non correct URL: ', url)

    def dm(self, data, rw):
        if rw: # delete url
            self._dmd(data)
            exit(1) # i can use exit without <from sys import exit>, didn't know about it

        if exists(self.file): # update chapters
            kk = self._ld()
            kk.update(data)
            self._dmd(kk)
        else: self._dmd(data) # create file

    def check(self):
        """
        - url: [chapter_1, chapter_2, chapter_3]              <- old chapters from json file
        + url: [chapter_1, chapter_2, chapter_3, chapter_4]   <- new chapter for manga
        """
        kk = self._ld()
        for url in (k for k in kk):
            soup = self._get_soup(url)
            manga = soup.find('dl', "chapter-list")
            chapters = kk[url]
            print('='*50)
            print(' ! URL: ', url)
            for chapter in manga.find_all('a', 'name'):
                urls = self.base + chapter.get('href')
                if urls not in chapters:
                    print(' + UPD: ', urls)
                    kk[url].append(urls)
            print('='*50)
        # updating json file, comment it to save old info
        self.dm(kk, True)

    def deli(self):
        url = input('URL: ')
        if url.startswith(self.base):
            kk = self._ld()
            k = [i for i in kk]
            if url in k:
                kk.pop(url, None)
                self.dm(kk, True)
            else: print('THIS URL not in ')
        else: print('NON correct URL: ', url)

    def _call_func(self, q):
        return {
            'c': self.check,
            'a': self.gen_json,
            'd': self.deli
        }.get(q, exit)()

    def main(self):
        mkd(BASE_DIR)
        q = input('[c]eck | [a]dd | [d]el: ')
        self._call_func(q)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--http", help="http proxy: '{host}:{port}'")
    parser.add_argument("--https", help="https proxy: '{host}:{port}'")
    args = parser.parse_args()

    proxy = args.http
    if proxy:
        proxy = {'http': proxy}
    else:
        proxy = args.https
        if proxy:
            proxy = {'https': proxy}

    ch = Check(proxy)
    try:
        ch.main()
    except KeyboardInterrupt:
        pass
