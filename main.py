import os
import jieba
import jieba.analyse
from wordcloud import WordCloud
from matplotlib import pyplot

font_path = r'C:\Windows\Fonts\msyh.ttc' # default for Windows
book_path = "./input/input.txt"          # encoded in utf8

userdict_path = "./tmp/userdict.txt"
stopwords_path = "./input/stopwords.txt"
stopwords_set = set(line.strip() for line in open(stopwords_path,"r", encoding="utf8"))

# get keywords
keywords = input("type keywords (separated by space): ").split()
print('got keywords: ', keywords)

# init user dict
userdict_file = open(userdict_path, "w+", encoding="utf8")
userdict_file.write("\n".join(keywords))
userdict_file.close()

# init jieba
jieba.load_userdict(userdict_path)

words_dict = {} # word cloud input

with open(book_path,"r",encoding="utf8") as f:
    for line in f.readlines():
        if all(line.find(e) >= 0 for e in keywords):
            words = filter(lambda x: x not in stopwords_set, jieba.cut(line.strip()))
            for word in words:
                if word not in words_dict:
                    words_dict[word] = 1
                else:
                    words_dict[word] += 1

word=WordCloud(
    background_color="white",
    max_font_size=100,
    min_font_size=10,
    max_words=30,
    random_state=50,
    font_path=font_path,
)

word.generate_from_frequencies(words_dict)
word.to_file("out.png")