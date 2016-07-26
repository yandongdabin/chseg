#!/usr/bin/python
#coding=utf-8
from __future__ import division
import sys
from scipy.optimize import fmin_bfgs,fmin_cg,fmin_l_bfgs_b
from utils import feature_id_factory,time_spend
from math import exp,log10
import random
import numpy as np
import codecs
import re
reload(sys)
sys.setdefaultencoding("utf-8")



class train_model(object):
    #feature_file为记录每一个句子feature的，feature_dict_file用于解码
    def __init__(self,feature_file_name,feature_dict_file):
        self.id_feature = feature_id_factory(feature_dict_file)
        feature_file = codecs.open(feature_file_name,"r","utf-8")
        self.feature_file_list = feature_file.readlines()
        feature_file.close()
        self.total_line_feature,self.total_feature_without_tags =  self.get_total_line_info()
        self.iii = 0
    def get_len(self):
        return self.id_feature.get_feature_no_dict_len()

    def get_total_line_info(self):
        print 'reading total line info from the file'
        idx = 0
        feature_file_list = self.feature_file_list
        feature_file_list_length = len(feature_file_list)
        total_line_feature = []
        total_feature_without_tags = []
         #下面的while循环，用来读取出下一句文字
        while idx < feature_file_list_length:
                #因为是新行，所以重置这一行的信息
                line_feature_dict = {}
                #重置这一行的特征，在文件里是FEA后对应的那一行，读取此行中出现的特征
                feature_without_tags = []
                #下面是读取每一行 读取<SEP>表示这一行已经读完
                while True:
                    words = feature_file_list[idx].strip().split()
                    idx = idx + 1
                    if(words[0]=='<FEA>'):
                        strs = re.findall("\[.+?\]",feature_file_list[idx])
                        for s in strs:
                            feature_without_tags.append(list(eval(s)))
                            #print s
                        idx = idx + 1
                        continue
                    if(words[0]=='<SEP>'):
                        break
                    line_feature_dict[words[0]] = words[1]
                total_line_feature.append(line_feature_dict)
                total_feature_without_tags.append(feature_without_tags)
        print 'reading over'
        return total_line_feature,total_feature_without_tags
    

    def goal_function(self,lamda):
        #代表的是特征的个数
        #读取的是不同的特征函数的编码
        feature_no_dict = self.id_feature.get_feature_no_dict()
        #读取的是语料库的编码
        feature_file_list = self.feature_file_list
        feature_file_list_length = len(feature_file_list)
        #用来存储每一行的信息
        line_feature_dict = {}
        
        delta = 1
        progress = 0
        #对每一个特征进行迭代
        #k 个形式是 tag_tag
        add_total = 0
        z = 0
        result = 0
        
        while_len = len(self.total_line_feature)
         #对每一句话进行处理
         #下面的while循环，用来读取出下一句文字
        for w_i in range(while_len):
                add_total = 0
                line_feature_dict = self.total_line_feature[w_i]
                feature_without_tags = self.total_feature_without_tags[w_i]
                #已经读完了一句话，下面开始分别进行处理
                for (key,value) in line_feature_dict.items():
                    add_total += lamda[int(feature_no_dict[key])]*int(value)
                #下面开始计算Z(X)
                l = len(feature_without_tags)+1 #有多少个字
                
                alpha = [[0 for i in range(4)] for j in range(l)]
#                 alpha_ = np.arange(4*l).reshape(-1,4)
#                 print alpha_
                alpha[0] = [1 for i in range(4)]
                #alpha = np.zeros((l,4),dtype='double')
                #alpha[0] = np.ones((1,4),dtype='double')
                 #计算转移矩阵   
                #初始化二维数组
                ch  = 'SBME'
                transfer_matrix = [[0 for i in range(4)] for j in range(4)]
                #transfer_matrix = np.zeros((4,4),dtype='double')
                 #对每一个字进行处理 计算 forward 概率
                for xi_idx in range(l-1):
                    #计算转移概率矩阵
                    for i in range(4):
                        for j in range(4):
                            prefix_bi = str(self.id_feature.get_tag_id(ch[i]+ch[j]))
                            #prefix_uni = str(self.id_feature.get_tag_id(ch[j]))
                            transfer_matrix[i][j] = 0
                            for xii in feature_without_tags[xi_idx]:
                                tmp = prefix_bi +"_"+str(xii)
                                #tmp2 = prefix_uni + "_" + str(xii)
                                if tmp in feature_no_dict:
                                    transfer_matrix[i][j]+=lamda[int(feature_no_dict[tmp])]
#                                 if tmp2 in feature_no_dict:
#                                     transfer_matrix[i][j]+=lamda[int(feature_no_dict[tmp2])]
                            transfer_matrix[i][j] = exp(transfer_matrix[i][j])
                    #print transfer_matrix
                     #计算 alpha_i
                    #alpha[xi_idx+1] = np.dot(alpha[xi_idx],transfer_matrix)
                    #print transfer_matrix
                    for i in range(4):
                        for j in range(4):
                            alpha[xi_idx+1][i] += alpha[xi_idx][j] * transfer_matrix[j][i]
                #print alpha[l-1]
                z=sum(alpha[l-1])
                #print add_total
                #print log10(z)
                if(z == 0.0): continue
                print add_total
                result += add_total - log10(z)
        #result += sum([(x*x)/(delta*delta) for x in lamda])        
        self.iii += 1
        if(self.iii % 100 == 0):
            print lamda
        #print result
        return result
                  
if __name__ == "__main__":
    model = train_model("output/feature_learned.txt","output/feature_dict.txt")
    
    lens= model.get_len()
    print lens
    lamda = [0.1 for i in range(lens)]
    #res = fmin_bfgs(model.goal_function,lamda,maxiter=2)
    bounds = [(0,1) for i in range(lens)]
    res =fmin_l_bfgs_b(model.goal_function, lamda,approx_grad = True,m=6)
    feature_no_list = model.id_feature.get_feature_no_dict().keys()
    file = codecs.open("model.txt","w",'utf-8')
      
    idx = 0
    for i in res:
        file.write(feature_no_list[idx]+"\t"+str(i)+"\n")
        idx += 1
    file.close()
    print res