import re
import json
import time
import jieba
import logging
import requests
import numpy as np
from urllib.parse import quote
from wordcloud import WordCloud
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt

jieba.setLogLevel(logging.INFO)
stopwords_path = "./input/stopwords.txt"
stopwords_set = set(line.strip()
                    for line in open(stopwords_path, "r", encoding="utf8"))


class DoubanCrawler:
    def __init__(self):
        self.headers = {
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0",
            'Host': 'book.douban.com'
        }  # book's headers
        self.book_search_url = "https://book.douban.com/j/subject_suggest?q="
        self.book_url = "https://book.douban.com/subject/%s/"
        self.book_comment_url = "https://book.douban.com/subject/%s/comments/?start=%d&limit=20&status=P&sort=new_score"
        self.words_dict = {}  # word cloud input

    def info_crawl(self, name, keywords, bg_image=None):
        name_str = self.__handle_name(name)  # url encodeded
        self.book_search_url += name_str
        self.book_url, num_str = self.__find_url(self.book_search_url)
        for i in range(0, 10):
            url = self.book_comment_url % (num_str, i*20)
            time.sleep(np.random.randint(1, 3))
            print("crawling page %d" % (i + 1), url)
            r = requests.get(url, headers=self.headers)
            soup = BeautifulSoup(r.content, 'lxml')
            comment_list = soup.find_all('span', class_='short')
            for ct in comment_list:
                line = ct.text.strip()
                if any(line.find(e) >= 0 for e in keywords):
                    words = filter(lambda x: x not in stopwords_set,
                                   jieba.cut(line))
                    for word in words:
                        if word not in self.words_dict:
                            self.words_dict[word] = 1
                        else:
                            self.words_dict[word] += 1

        self.__comment_to_txt(name, comment_list)
        self.__plot_wordcloud(name)

    def __plot_wordcloud(self, name):
        print("plot wordcloud...")
        word_cloud = WordCloud(
            scale=10,
            font_path='C:/Windows/Fonts/msyh.ttc',
            background_color="white", width=1000, height=1000
        ).generate_from_frequencies(self.words_dict)
        file_name = "./output/{}.png".format(name)
        word_cloud.to_file(file_name)
        plt.imshow(word_cloud, interpolation='bilinear')
        plt.axis('off')
        plt.show()

    def __comment_to_txt(self, name, clist):
        file_name = "./output/{}.txt".format(name)
        with open(file_name, 'w+', encoding='utf-8') as f:
            for ct in clist:
                f.write(ct.text)
            f.close()

    def __handle_name(self, name):
        return str(quote(name))

    def __find_url(self, url):
        r = requests.get(url, headers=self.headers)
        json_data = json.loads(r.text)
        address_num = re.search('[0-9]+', json_data[0]['url'])
        print(self.book_url % address_num.group(0))
        return self.book_url % address_num, address_num.group(0)


if __name__ == '__main__':
    book_name = input("type book name: ")
    print('got boot name: ', book_name)
    keywords = input("type keywords (separated by space): ").split()
    print('got keywords: ', keywords)
    crawler = DoubanCrawler()
    crawler.info_crawl(book_name, keywords)
