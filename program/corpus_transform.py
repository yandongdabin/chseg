
#coding=utf-8

import codecs
import sys
import re
reload(sys)
sys.setdefaultencoding('utf-8')
#每一行作为一个训练单位，行首加上BOS行末加上EOS
#现在
"""
将原始的训练语料进行转化，转化为标签的形式
现在的标签有 ：S（单字） B（开头） M（中间） E（结尾）
输出后的形式
<BOS>
word tag
...
<EOS>
...
...
<BOS>
...
<EOS>
"""

PUNCTUATION = ('。','，','！','《','》','％','￥','＃','（','）','＆','×','｀','～','｜','、','／','？','“','”',
               '－','——','＠','：','；','、')


def gbk2utf8(input_file,output_file):
    with codecs.open(input_file,'r','gbk') as f,codecs.open(output_file,'w','utf-8') as f2:
        f2.write(f.read());           
def character_tagging(input_file, output_file,own=True):
  input_data = codecs.open(input_file, 'r','utf-8')
  output_data = codecs.open(output_file, 'w',"utf-8")
  data = input_data.readlines()
  lens = len(data)
  i=0
  for line in data:
    if(own):
        output_data.write("<BOS>\n")
    i+=1
    if(i%1000==0):
        print 'complete %d%%' %round(i*100/lens+1)
    word_list = line.strip().split()
    for word in word_list:
        pos = word.index('/')
        tag = word[pos+1:]
        if(tag=='m' or tag == 't'):
            continue
        word = word[:pos]
        if word in PUNCTUATION:
            continue
        if len(word) == 1:
            output_data.write(word + "\tS\n")
            continue
        else:
            output_data.write(word[0] + "\tB\n")
        for w in word[1:len(word)-1]:
            output_data.write(w + "\tM\n")
        output_data.write(word[len(word)-1] + "\tE\n")
    if(own):
        output_data.write("<EOS>\n")
    else:
        output_data.write("\n")
  input_data.close()
  output_data.close()
  print 'transform corpus complete'
  