# -*- coding: utf-8 -*-
from __future__ import division
import codecs
from corpus_transform import PUNCTUATION
def change_predict_file(file_name,output_file):
    print 'start change the predict file to i can identify'
    with codecs.open(file_name,'r','utf-8') as f:
        lines = f.readlines()
    output = codecs.open(output_file,'w','utf-8')
    output_right = codecs.open('right.txt','w','utf-8')
    for line in lines:
        if line.strip() == '':
            continue
        word_list = line.strip().split()
        word_line = ''
        word_line_right = ''
        for word in word_list:
            pos = word.index('/')
            tag = word[pos+1:]
            if(tag=='m' or tag == 't'):
                continue
            word = word[:pos]
            if word in PUNCTUATION:
                continue
            word_line+=word
            word_line_right=word_line_right + '\t' + word
        output.write(word_line+'\n')
        output_right.write(word_line_right+'\n')
    output.close()
    output_right.close()
    print 'change over'
def calc_precision(result_file,right_file):
    
    with codecs.open(result_file,'r','utf-8') as f1,codecs.open(right_file,'r','utf-8') as f2:
        result = f1.readlines()
        right = f2.readlines()
    idx1 = 0
    idx2 = 0 
    len1 = len(result)
    len2 = len(right)
    cnt = 0
    total_result = 0
    total_right = 0
    while(idx1<len1 and idx2 < len2):
        words1 = result[idx1]
        words2 = right[idx2]
        word_list1 = words1.strip().split()
        word_list2 = words2.strip().split()
        word_len1 = len(word_list1)
        word_len2 = len(word_list2)
        total_result+=word_len1
        total_right+=word_len2
        for word in word_list1:
            if word in word_list2:
                cnt += 1
        idx1+=1
        idx2+=1
    print 'precision =  %f' %(cnt/total_result)
    print 'recall = %f' %(cnt/total_right) 
    print 'f-measure = %f' %(2*cnt/(total_result+total_right))
            
if __name__ == '__main__':
    change_predict_file('corpus_predict.txt','testtest.data')
    #calc_precision('result.txt','right.txt')
        