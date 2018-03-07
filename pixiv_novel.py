#!/usr/bin/env PYTHONIOENCODING=UTF-8 python3
# -*- coding: utf-8 -*-
import sys
import io
import re
from robobrowser import RoboBrowser
from bs4 import BeautifulSoup

#タグ除去用
p = re.compile(r"<[^>]*?>")
# [jump:1]形式除去用
jump = re.compile(r"\[jump:.+\]")
#ファイルエンコード設定用
character_encoding = 'utf8'
pixiv_url = 'https://www.pixiv.net'
browser = RoboBrowser(parser='lxml', history=True)
browser.open('https://accounts.pixiv.net/login')
form = browser.get_forms('form', class_='')[0]
form['pixiv_id'] = '***'
form['password'] = '***'
browser.submit_form(form)
page = 1
target_url_bkm = 'https://www.pixiv.net/novel/bookmark.php?rest=hide&p='
browser.open('https://www.pixiv.net')

title = browser.find(class_='user-name').string
print(title)
print('=====================================================')
for i in range(1):
    print(target_url_bkm + str(page + i))
    browser.open(target_url_bkm + str(page + i))

    novel_items = browser.find(class_='novel-items')

    for novel in novel_items.find_all(class_='_novel-item'):
        soup = BeautifulSoup(str(novel), "html.parser")
        #print(soup.find('h1', class_='title').a)
        #print(novel)
        a_tag = novel.find('h1', class_='title').find('a')

        # novel info
        novel_url = a_tag.get('href')
        novel_title = a_tag.get_text()

        if novel_title != "-----":
            # user info
            user_tag = novel.find('a', class_='user')
            user = user_tag.get_text()
            data_user_id = user_tag.get('data-user_id')
            print(data_user_id)

            series_title_elm = novel.find('a', class_='series-title')
            if novel.find('a', class_='series-title') is None:
                series_title = ''
            else:
                series_title = series_title_elm.get_text()

            novel_id = novel_url.replace('/novel/show.php?id=', '')
            novel_file_title = ''
            if series_title != '':
                novel_file_title = user + '(' + data_user_id + ')' + ' -- [' + series_title + '] ' + novel_title + '(' + novel_id + ')'
            else:
                novel_file_title = user + '(' + data_user_id + ')' + ' -- ' +  novel_title + '(' + novel_id + ')'
            print(novel_file_title)
            print(novel_url)

            # tag
            novel_tag_elm = novel.find('ul', class_='tags')
            novel_tag_soup = BeautifulSoup(str(novel_tag_elm), "html.parser")
            #print(novel_tag_soup)
            tag_list = list()
            novel_tags = ''
            for tag in novel_tag_soup.find_all('li'):
                tag.find(class_='tag-icon').decompose()
                tag_list.append(tag.find('a').get_text())

            novel_tags = '|'.join(tag_list)
            print(novel_tags)

            #詳細画面に移動
            browser.open(pixiv_url + novel_url)
            unit = browser.find(class_='_unit')
            if unit.find(class_='title') is None:
                continue

            title = unit.find(class_='title').string
            print(title)
            unit_soup = BeautifulSoup(str(unit), "html.parser")
            unit_soup_caption = unit_soup.find(class_='caption')
            unit_soup_caption_not_br = str(unit_soup_caption).replace('<br/>','\r\n')
            caption = p.sub("", unit_soup_caption_not_br)
            ##print(caption)
            print('-----------------------------------------------------')
            unit_soup_novel_pages = unit_soup.find(class_='novel-pages')
            #不要要素削除
            unit_soup_novel_pages.find('div', class_='_reaction-buttons-container').decompose()
            # 改行は不要、特定タグを改行とする
            unit_soup_novel_pages_not_br = str(unit_soup_novel_pages).replace('[newpage]','\r\n')
            # タグ削除
            novel_pages = p.sub("", unit_soup_novel_pages_not_br)
            novel_pages = jump.sub("", novel_pages)

            with io.open(novel_file_title.replace('/','／') + '.txt', 'w', encoding=character_encoding) as file:
                file.write(novel_file_title + '\r\n' + novel_url +'\r\n\r\n-----------------------------------------------------\r\n' + novel_title +'\r\n' + '-----------------------------------------------------'+ '\r\n')
                file.write(novel_tags + '\r\n' + '-----------------------------------------------------' + '\r\n' )
                file.write(caption + '\r\n' + '-----------------------------------------------------' + '\r\n' )
                file.write(novel_pages + '\r\n' + '=====================================================' + '\r\n' )

            print('=====================================================')
