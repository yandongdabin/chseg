#!/usr/bin/python
#coding=utf-8
import re
import codecs
from utils import get_feature_per_line,feature_id_factory,get_unicode
"""
用维特比算法根据得到的概率值进行预测
"""
class model_pridict(object):
    def __init__(self,model_file_name,feature_file_name,template_file):
        self.model_dict = {}
        self.id_factory = feature_id_factory(feature_file_name)
        self.template_file = template_file
        lines = ()
        try:
            file = codecs.open(model_file_name,"r","utf-8")
            lines = file.readlines()
            file.close()
        except Exception,e:
            print e
            print 'read model file error ,check if it exists'
        for line in lines:
            words = line.strip().split()
            self.model_dict[words[0]] = float(words[1])
    def predict_file(self,filename):
        with codecs.open(filename,'r','utf-8') as f:
            lines = f.readlines()
        total  = ''
        #print len(lines)
        f = codecs.open('result.txt','w','utf-8')
        line_num = 1
        for line in lines:
            #print 'split the %d line' %line_num
            res =  self.predict(line)
            f.write(res)
            line_num+=1
        f.close()
    def predict(self,x):
        state = 'BMES'
        delta = [[0 for i in range(4)] for j in range(len(x)+1)]
        #用来回溯最优解
        fi = [[0 for i in range(4)] for j in range(len(x)+1)]
        delta[0] = [0 for i in range(4)]
        
        feature_list = get_feature_per_line(x,self.id_factory,self.template_file)
        #print feature_list
        len_x = len(x)
        #对每个汉字进行处理
        for i in range(1,len_x+1):
            for j in range(4):
                idx = 0
                delta[i][j] = -100000
                for k in range(4):
                    #bi_id = self.id_factory.get_tag_id(state[k]+state[j])
                    uni_id = self.id_factory.get_tag_id(state[j])
                    pro = 0
                    for l in feature_list[i-1]:
                        #bi_str =  str(bi_id)+"_"+str(l)
                        uni_str = str(uni_id)+"_"+str(l)
#                         if(bi_str in self.model_dict):
#                             pro += self.model_dict[str(bi_id)+"_"+str(l)]
                        if(uni_str in self.model_dict):
                            pro += self.model_dict[str(uni_id)+"_"+str(l)] 
                    tmp = delta[i-1][k] + pro
                    if(delta[i][j]<tmp):
                        idx = k
                        delta[i][j] = tmp
                fi[i][j] = int(idx)
        result = []
        #print delta
        pos = fi[len_x][delta[len_x].index(max(delta[len_x]))]
        #print pos
        result.append(state[pos])
        #print fi
        for i in range(len_x-1,0,-1):
            pos = fi[i+1][pos]
            result.append(state[pos])
        result.reverse()
        #print result
        if(len_x <= 1):
            result[0] = 'S'
        else:
            if(result[1]!='E' or result[1]!='M'):
                result[0] = 'S'
            if(result[1]=='E' or result[1]=='M'):
                result[0] = 'B'
        if(len_x >= 2):
            if(result[len_x-2]!='B' and result[len_x-2]!='M'):
                result[len_x - 1] = 'S'
            else:
                result[len_x - 1] = 'E'
        #print result
        res = self.output_seq_with_tag(result, x)
        res_str = ''
        for r in res:
            res_str = res_str + r + '\t'
        return res_str
    def output_seq_with_tag(self,tags,x):
        res = []
        tmp = ""
        for i in range(len(tags)):
            tag = tags[i]
            if(tag == 'S'):
                if(tmp!=""):
                    res.append(tmp)
                    tmp = ""
                res.append(x[i])
            elif(tag=="B"):
                if(tmp!=""):
                    res.append(tmp)
                    tmp = ""
                tmp+=x[i]
            elif(tag=='M'):
                tmp+= x[i]
            elif(tag=='E'):
                tmp+=x[i]
                res.append(tmp)
                tmp=""
        #for i in range(len(res)):
            #print res[i]
            #res[i] = get_unicode(res[i])
            #print res[i]
        return res
if __name__=='__main__':
    x=u'迈向充满希望的新世纪江泽民'
    a = model_pridict("output/mymodel.txt","output/feature_dict.txt",'feature.txt')
    a.predict_file('test.data')