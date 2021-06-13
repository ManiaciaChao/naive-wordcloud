# douban crawler
import wordcloud
import jieba.analyse
from collections import Counter
import numpy as np
from wordcloud import WordCloud
import jieba.posseg as psg
from matplotlib import colors
import matplotlib
import networkx as nx
import matplotlib.pyplot as plt
import jieba
from .crawler import DoubanCrawler

# 对目标书籍爬取的函数定义过程
# 导入相关库
from bs4 import BeautifulSoup
import requests
import sys


class Download:
    def __init__(self, website_url, book_url):
        self.website_url = website_url
        self.book_url = book_url
        self.chapters_number = 0  # 定义章节数目
        self.chapters_url = []  # 定义章节地址列表
        self.chapters_name = []  # 定义章节名字列表

    def download_url(self):
        response = requests.get(self.book_url)  # 发送获得网页页面的请求并获得反映内容
        html = response.text.encode("latin1").decode(
            "gbk")  # 将网页文本内容转换为latin1编码
        total_text = BeautifulSoup(html, 'lxml')
        chapter_lists = total_text.find_all('div', 'list')  # 获取书籍章节所在网页编码
        chapter_list_content = BeautifulSoup(str(chapter_lists), 'lxml')
        a = chapter_list_content.find_all('a')  # 获取书籍每个章节的网页html
        for i in a:
            self.chapters_name.append(i.string)
            self.chapters_url.append(self.website_url+i.get('href'))
        self.chapters_number = len(a)  # 计数该书籍所有章节数

    def download_content1(self, chapter_url):  # 编写13章以前的内容获取函数
        response = requests.get(chapter_url)
        response.encoding = 'gbk'
        html = response.text
        total_text = BeautifulSoup(html, 'lxml')
        texts = total_text.find_all('div', class_='width')  # 获取小说每章具体内容
        content_text = BeautifulSoup(str(texts), 'lxml')
        div = content_text.find_all('p')  # 13章以前的小说内容标签为p
        content = ''  # 将小说每章内容存到字段content中
        for i in div:
            if i.string is not None:
                content = content+i.string + '\n\n'
        return content

    def download_content2(self, chapter_url):  # 编写13章以后的内容获取函数
        response = requests.get(chapter_url)
        response.encoding = 'gbk'
        html = response.text
        total_text = BeautifulSoup(html, 'lxml')
        texts = total_text.find_all('div', class_='width')  # 获取小说每章具体内容
        content_text = BeautifulSoup(str(texts), 'lxml')
        div = content_text.find_all('div')  # 13章以后的小说内容标签为div
        content = ''  # 将小说每章内容存到字段content中
        for i in div:
            if i.string is not None:
                content = content+i.string + '\n\n'
        return content

    def writer(self, chapter_name, chapter_content, filepath):  # 定义小说内容写入txt文件的函数
        with open(filepath, 'a', encoding='utf-8') as file_object:  # 将其编码为'utf-8'格式
            file_object.write(chapter_name + '\n')  # 写入章节名
            file_object.writelines(chapter_content)  # 写入每章节内容
            file_object.write('\n\n')


if __name__ == '__main__':  # 在当前模块内执行函数
    website_url = "http://www.mingzhuxiaoshuo.com"
    book_url = "http://www.mingzhuxiaoshuo.com/jinxiandai/99"  # 输入平凡的世界书籍所在的网址
    download1 = Download(website_url, book_url)
    download1.download_url()
    print("开始下载目标书籍：")
    for i in range(download1.chapters_number):
        if i < 12:
            download1.writer(download1.chapters_name[i], download1.download_content1(
                download1.chapters_url[i]), '平凡的世界.txt')
            sys.stdout.write("已下载：%.3f%%" % float(
                100*((i+1)/download1.chapters_number))+'\r')
            # 将光标的位置退到本行，标准化输出
        else:
            download1.writer(download1.chapters_name[i], download1.download_content2(
                download1.chapters_url[i]), '平凡的世界.txt')
            sys.stdout.write("已下载：%.3f%%" % float(
                100*((i+1)/download1.chapters_number)) + '\r')
        sys.stdout.flush
    print('\n下载完成')  # 让缓冲区的内容输出

# 核心代码实现部分
# 导入相关库并设置好matplot的格式
matplotlib.rcParams['font.sans-serif'] = ['SimHei']
# 读取文本


def read_txt(filename):
    with open(filename, 'r+', encoding='utf-8') as f:
        text = f.read()
    return text

# 定义过滤词列表


def stopwordslist(filepath):
    stopwordslist = [line.strip() for line in open(
        filepath, 'r', encoding='utf-8').readlines()]
    return stopwordslist

# 定义有效词列表


def write_txt(filename):
    words_initial = jieba.lcut(read_txt(filename))
    words_final = []
    stopwords = stopwordslist('stop.txt')
    for word in words_initial:
        if len(word) == 1:  # 过滤单个字的词语
            continue
        elif word not in stopwords:  # 过滤停用词里的词语
            words_final.append(word)
    word_count_dict = Counter(words_final)  # 利用Counter函数形成词频字典
    wclist = list(word_count_dict.items())  # 将字典转化为列表形式
    sorted(wclist, key=lambda x: x[1], reverse=True)  # 根据词频对字典进行从大到小的排序
    with open('词频统计.txt', 'w') as f:  # 将词频结果写入txt文件
        for i in range(len(word_count_dict.items())):
            word, count = wclist[i]
            f.writelines("{0:<5}{1:>5}\n".format(word, count))
        return word_count_dict


# 生成整本书的词云


def create_wordcloud(filename):
    text = write_txt(filename).keys()
    wl_space_split = " ".join(text)
    color_list = ['#87CEFA', '#0000CD',
                  '#ADD8E6', '#1E90FF', '#00BFFF']  # 设置颜色格式
    colormap = colors.ListedColormap(color_list)
    wcloud = WordCloud(background_color="white",  # 设置词云图的格式
                       width=1000,
                       height=800,
                       margin=2,
                       font_path='C:\\WINDOWS\\FONTS\\MSYH.TTC',
                       colormap=colormap,
                       max_words=250
                       ).generate(wl_space_split)
    plt.imshow(wcloud, interpolation="bilinear")
    plt.axis("off")
    plt.title("《平凡的世界》词云")
    plt.show()

# 生成人物关系图、


def create_relationship(filename, Names):
    relations = {}
    para_total = (read_txt(filename)).split('\n')  # 定义两个人物直接的关系权重度
    for para_each in para_total:
        for name1 in Names:
            if name1 in para_each:
                for name2 in Names:
                    if name2 in para_each and name2 != name1 and (name2, name1) not in relations:
                        relations[(name1, name2)] = relations.get(
                            (name1, name2), 0)+1
    basic = max([appearance_times for appearance_times in relations.values()])
    relations = {namepair: appearance_times/basic for namepair,
                 appearance_times in relations.items()}
    plt.figure(figsize=(15, 15))
    G = nx.Graph()
    for namepair, weight in relations.items():
        G.add_edge(namepair[0], namepair[1], weight=weight)
    # 筛选权重大于0.7的边
    elarge = [(u, v) for (u, v, d) in G.edges(data=True) if d['weight'] > 0.7]
    # 筛选权重大于0.2小于0.7的边
    emidle = [(u, v) for (u, v, d) in G.edges(data=True)
              if (d['weight'] > 0.2) & (d['weight'] <= 0.7)]
    # 筛选权重大于0小于0.2的边
    esmall = [(u, v) for (u, v, d) in G.edges(data=True)
              if (d['weight'] <= 0.2) & (d['weight'] > 0)]
    # 设置图形格式
    pos = nx.spring_layout(G)
    # 设置节点样式
    nx.draw_networkx_nodes(G, pos, node_color='lightcyan',
                           alpha=0.8, node_size=1200)
    # 设置权重大于0.7的边的格式
    nx.draw_networkx_edges(G, pos, edgelist=elarge,
                           width=3.0, alpha=0.9, edge_color='darkblue')
    # 设置权重在0.2~0.7的边的格式
    nx.draw_networkx_edges(G, pos, edgelist=emidle,
                           width=2.0, alpha=0.6, edge_color='royalblue')
    # 设置权重在0~0.2的边的格式
    nx.draw_networkx_edges(G, pos, edgelist=esmall,
                           width=1.0, alpha=0.4, edge_color='cornflowerblue')
    nx.draw_networkx_labels(G, pos, font_size=12)
    plt.axis('off')
    plt.title("小说人物关系权重图")
    plt.show()

# 生成小说人物重要程度饼状图


def create_character_importance(filename, Names):
    plt.figure(figsize=(12, 10))
    x = Names
    y = []
    for i in x:
        i0 = write_txt(filename).get(i, 0)
        y.append(i0)
    # 设置颜色格式
    colors = ['darkblue', 'blue', 'royalblue', 'dodgerblue',
              'deepskyblue', 'lightskyblue', 'lightblue', 'lightcyan']
    plt.pie(x=y, labels=x, colors=colors, autopct='%1.1f%%')
    plt.title("小说人物权重图")
    plt.show()


def create_character_wordcloud(filename, Names):
    font_path = r'C:\Windows\Fonts\msyh.ttc'  # default for Windows

    userdict_path = "userdict.txt"
    stopwords = stopwordslist('stop.txt')
    stopwords_set = set(line.strip()
                        for line in open(stopwords, "r", encoding="utf8"))

    # init user dict
    userdict_file = open(userdict_path, "w+", encoding="utf8")
    userdict_file.write("\n".join(Names))
    userdict_file.close()

    # init jieba
    jieba.load_userdict(userdict_path)

    words_dict = {}  # word cloud input

    with open(filename, "r", encoding="utf8") as f:
        for line in f.readlines():
            if all(line.find(e) >= 0 for e in Names):
                words = filter(lambda x: x not in stopwords_set,
                               jieba.cut(line.strip()))
                for word in words:
                    if word not in words_dict:
                        words_dict[word] = 1
                    else:
                        words_dict[word] += 1

    word = WordCloud(
        background_color="white",
        max_font_size=100,
        min_font_size=10,
        max_words=30,
        random_state=50,
        font_path=font_path,
    )

    word.generate_from_frequencies(words_dict)
    word.to_file("out.png")


def main(book, Names):  # 将所有函数再定义为一个整体函数
    filename = "{}.txt".format(book)
    read_txt(filename)
    write_txt(filename)
    create_wordcloud(filename)
    create_character_importance(filename, Names)
    create_relationship(filename, Names)
    create_character_wordcloud(filename, Names)
    crawler = DoubanCrawler()
    crawler.info_crawl(book, Names)


# 输入目标书籍
book = '平凡的世界'
# 输入目标书籍内主要人物
character_str = "孙少平，孙少安，贺秀莲，孙玉厚，田润叶，郝红梅，孙玉亭，田润生，田福军，田晓霞"
character = character_str.split('，')
main(book, character)
