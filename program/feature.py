#!/usr/bin/python
#coding=utf-8
import codecs
import re
import sys
import utils
from utils import queue,time_spend,feature_id_factory,read_feature_file,print_unicode
import utils
reload(sys)
sys.setdefaultencoding("utf-8")

threshold = 1

"this module is about how to get the featue from the corpus"

       
@time_spend           
def select_feature(input_file_name,output_file_name,model_dict):
   
    #默认记录前后五步的历史
    history_size = 5
    future_size = history_size
    history_queue = queue(history_size)
    feature_queue = queue(future_size)
    #查看配置文件中的特征值
    unigram = model_dict["U"]
    input_file = codecs.open(input_file_name,"r","utf-8")
    output_file = codecs.open(output_file_name,"w",'utf-8')
    input_data = input_file.readlines()
    #保证进度用
    progress=0
    lens = len(input_data)
    #记录当前预读到了第几行
    #初始化为指向第一个汉字
    idx = 1
    #从这个对象里面进行特征的编码和解码
    id_factory = feature_id_factory()
    #每一行存储一个特征字典
    line_feature_dict = {}
    
    total_line_feature_dict = []
    total_feature_without_tags = []
    #没有状态信息的特征
    feature_without_tags = []
    #全局特征，用来存储特征函数
    total_feature_dict = {}
    enter_another_line = False
    for line in input_data:
        words = line.strip().split()
        #print print_unicode(line)
        #print print_unicode(words)
        if words[0]=='<BOS>':
            idx+=1
            #预读取几行到feature_queue
            enter_another_line = False
            history_queue.clear()
            feature_queue.clear()
            for j in xrange(future_size-1):
                if(idx>=lens): break
               
                cur_words = input_data[idx].strip().split()
                
                #注意，进入此循环，代表一定发生了预读
                idx += 1
                if(cur_words[0] == '<EOS>'):
                    enter_another_line = True   
                    break
                feature_queue.push(input_data[idx-1])
            continue
       
            
        if words[0]=="<EOS>":
            feature_queue.clear()
            history_queue.clear()
            if(len(feature_without_tags) == 0):
                continue
            total_line_feature_dict.append(line_feature_dict)
            total_feature_without_tags.append(feature_without_tags)
            line_feature_dict = {}
            feature_without_tags = []
            
            #当读到此处的时候，idx肯定指向了下一个<BOS> enter_another_line肯定为True
            #所以要idx+1,跳过读取下一个<BOS>
            idx+=1
            continue
          #预读下一行的信息
        if(enter_another_line == False and idx<lens):
            cur_words = input_data[idx].strip().split()
            idx+=1
            if cur_words[0] != '<EOS>' and cur_words[0]!='<BOS>':
                feature_queue.push(input_data[idx-1])
                
            if(cur_words[0] == '<EOS>'):
                enter_another_line = True
        progress+=1
      
        #输出进度，可以调整后面的值，否则变化会太快或者太慢
        if(progress%100000==0):
            print "extract feature complete %d%%" %round((progress*100/lens+1))
        feature_list,total_feature_without_tag =  utils.encode_feature(words,unigram,history_queue,feature_queue,id_factory)
              #!!important
        feature_queue.pop()
        for cur_feature in feature_list:
            if(cur_feature not in line_feature_dict):
                line_feature_dict[cur_feature] = 1
            else:
                line_feature_dict[cur_feature]+=1
            if(cur_feature not in total_feature_dict):
                total_feature_dict[cur_feature] = 1
            else:
                total_feature_dict[cur_feature] += 1
        feature_without_tags.append(total_feature_without_tag)
        history_queue.push(words)
#     print 'writing features to file...'
#     output_file.write(str(len(feature_dict))+"\n")
#     for key in feature_dict:
#         output_file.write(key+"\t"+str(feature_dict[key])+"\n")
    

    print 'writing features into disk ...'
    total_feature_dict_filename = 'output/total_feature_with_tags.txt'
    total_feature_dict_file = codecs.open(total_feature_dict_filename,"w","utf-8")
    no = 0
    for key in total_feature_dict:
        if total_feature_dict[key] >= threshold:
            total_feature_dict_file.write(key+"\t"+str(no)+"\n")
            no+=1
    for i,item in enumerate(total_line_feature_dict):
        output_file.write("<FEA>\n")
        for item in total_feature_without_tags[i]:
            output_file.write(str(item)+"\t")
        output_file.write("\n")
        for key in total_line_feature_dict[i]:
            if(total_feature_dict[key] >= threshold):
                output_file.write(str(key)+"\t"+str(total_line_feature_dict[i][key])+"\n")
        output_file.write("<SEP>\n")
    total_feature_dict_file.close()
    output_file.close()
    id_factory.write_file("output/feature_dict.txt")  
    print 'extract feature complete!!'     
if __name__ == "__main__":
    #feature_selection("output.txt", "test_output.txt")
    res = read_feature_file("feature.txt")
    select_feature("corpus_transformed.txt","output/feature_learned.txt",res)