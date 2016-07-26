#coding=utf-8
from time import time
import codecs
import re


"""
对特征进行编码
"""
class feature_id_factory(object):
    #默认不读取文件，试用于提取特征值的时候
    def __init__(self,feature_file=None,template_file = None):
        self.feature_dict = {}
        self.id_dict = {}
        self.id = 0
        self.total_feature_size = 0
        self.feature_no_dict = {}
        #状态标记
        self.statetag = {}
        str = 'BMES'
        for i in range(4):
            self.statetag[str[i]] = i
        for i in range(4):
            for j in range(4):
                self.statetag[""+str[i]+str[j]] = i + j + 4
        
        if feature_file is not None:
            print 'reading feature_dict file %s from the disk..' %feature_file
            file = codecs.open(feature_file,"r","utf-8")
            for line in file.readlines():
                words = line.strip().split()
                self.feature_dict[words[0]] = words[1]
                self.id_dict[words[1]] = words[0]
            file.close()
            print 'reading ok'
            
            #读取所有的特征
            tmp_feature_list = codecs.open("output/total_feature_with_tags.txt","r","utf-8").readlines()
            for line in tmp_feature_list:
                words = line.strip().split()
                self.feature_no_dict[words[0]] = words[1]
            self.total_feature_size = len(self.feature_no_dict)
        self.template_file = template_file
    #根据特征字符串获得编码
    def get_feature_id(self,feature):
        res = None
        if feature not in self.feature_dict:
            self.feature_dict[feature] = self.id
            self.id_dict[self.id] = feature
            res = self.id
            self.id = self.id+1
        else:
            res = self.feature_dict[feature]
        return res
    #得到所有的f的key 
    def get_feature_no_dict(self):
        return self.feature_no_dict 
    #得到特征的长度
    def get_feature_no_dict_len(self):
        return self.total_feature_size
    #得到状态转移的id
    def get_tag_id(self,tag):
        #print tag
        return self.statetag[tag]
    #根据特征得到id
    def get_feature_from_id(self,feature_id):
        return self.id_dict[feature_id]
    #得到当前的长度
    def len(self):
        return len(self.feature_dict)
    #当当前的信息写入到文件
    def write_file(self,filename):
        try:
            write_file = codecs.open(filename,"w","utf-8")
            for key in self.feature_dict:
                write_file.write(str(key)+"\t"+str(self.feature_dict[key])+"\n")
            write_file.close()
        except Exception,e:
            print e
            print 'write the feature dictionary error'
            return None
#定义这个队列来记录行的历史
class queue(object):
    def __init__(self,size):
        self.data = []
        self.size = size
        self.real_size = 0
    def push(self,data):
        self.data.append(data)
        self.real_size+=1
        if(len(self.data) > self.size):
            self.data.pop(0)
            self.real_size-=1
    def pop(self):
        if(self.real_size>0):
            self.real_size-=1
            return self.data.pop(0)
    def get(self,idx):
        real_idx = idx
        if(idx < 0):
            real_idx = self.real_size + idx
        if(idx > 0 ):
            real_idx -=1
        if(real_idx >= self.real_size or real_idx <0):
            return None
        return self.data[real_idx]
    def print_queue(self):
        s = str(self.data)
        ss = s.decode("unicode_escape")
        print ss.encode("UTF-8")
    def clear(self):
        self.data = []
        self.real_size = 0
    def __getattr__(self,attr):
        return getattr(self.data,attr)

"""
对特征进行编码
基本的形式 是 tag#tag_tag#single

"""
def encode_feature(words,unigram,history_queue,future_queue,id_factory,with_state=True):
    
    #history_queue.print_queue()
    #future_queue.print_queue()
    #print words[0]
    total_feature = []
    total_feature_without_tag = []
    
    itemNamePrefix = 'U0'
    for (item_idx,item) in enumerate(unigram):
        itemName = itemNamePrefix + str(item_idx)+":"
        cur_feature = ""
        delimeter = ""
        if(len(item)>1):
            delimeter = "/"
        for tp in item:
            i_tp = [int(itp) for itp in tp]
            #超前读
            if(i_tp[0] > 0 ): 
                fwords = future_queue.get(i_tp[0])
                if(fwords is not None):
                    cur_feature+=fwords[i_tp[1]]+delimeter
                else:
                    #cur_feature+=""
                    cur_feature = ""
                    break
            elif(i_tp[0]==0):
                cur_feature+=words[i_tp[1]]+delimeter
            #读取历史
            else:
                oldwords = history_queue.get(i_tp[0])
                if(oldwords is not None):
                    cur_feature+=oldwords[i_tp[1]]+delimeter
                else:
                    #cur_feature+=""
                    cur_feature = ""
                    break
        if cur_feature is "":continue
        cur_feature = itemName+cur_feature
        feature_id = id_factory.get_feature_id(cur_feature)
        if feature_id not in total_feature_without_tag:
            total_feature_without_tag.append(feature_id)
        #是否需要对状态进行编码
        if(with_state == True):
            prefix_unigram =  words[1]
            former = history_queue.get(0)
            uni_tag_id = id_factory.get_tag_id(prefix_unigram)
            uni_str = str(uni_tag_id)+"_"+str(feature_id)
            #print uni_str
            if uni_str not in total_feature:
                total_feature.append(uni_str)
#             if bi_str not in total_feature:
#                 total_feature.append(bi_str)
    #prinprint total_feature   
    return total_feature,total_feature_without_tag   

"""
新增一个函数，用来预测时从输入的句子中读取信息
未测试.....
"""
def get_feature_per_line(line,id_factory,tempalte_file):
    history_size = 5
    history_queue = queue(history_size)
    future_queue = queue(history_size)
    #根据模板提取当前字的特征 当前默认处理的是 unigram
    feature_template = read_feature_file(tempalte_file)["U"]
    total_feature = []
    cur_reading_pos = 1
    #print line
    for i in range(history_size):
        if cur_reading_pos >= len(line):break
        future_queue.push(line[cur_reading_pos])
        cur_reading_pos+=1
    for word in line:
        #history_queue.print_queue()
        #future_queue.print_queue()
        none,cur_word_feature = encode_feature(word,feature_template,history_queue,future_queue,id_factory,False)
        total_feature.append(cur_word_feature)
        history_queue.push(word)
        future_queue.pop()
        if cur_reading_pos < len(line):
            future_queue.push(line[cur_reading_pos])
            cur_reading_pos += 1
        
    return total_feature   
        
"""
装饰器，用来统计程序运行的时间
"""  
def time_spend(f):
    def wrapper(*args,**kargs):
        now = time()
        try:
            return f(*args,**kargs)
        finally:
            print 'time spend %s seconds' %round((time()-now),2)
    return wrapper
"""
用来读取特征的配置文件 feature.txt
"""
def read_feature_file(model_file_name):
    model_file = codecs.open(model_file_name,"r")
    lines = model_file.readlines()
    res = {"B":[],"U":[]}
    for line in lines:
        if(line[0]=='#'): continue
        if(line[0]=='U'):
            pattern = "\[(\-?\d+),(\-?\d+)\]"
            ret = re.findall(pattern,line)  
            res["U"].append(ret)
        #此处Bigram采用默认的，不做处理
        if(line[0]=="B"):
            res["B"].append("B")
    model_file.close()
    #print res
    return res    
def print_unicode(si):
    s = str(si)
    ss = s.decode("unicode_escape")
    print ss.encode("UTF-8") 
def get_unicode(si):
    s = str(si)
    ss = s.decode("unicode_escape")
    return ss.encode("UTF-8") 
if __name__ =='__main__':
    q = queue(5)
    for i in range(10):
        q.push(i)
        q.print_queue()