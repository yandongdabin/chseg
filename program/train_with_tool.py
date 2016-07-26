#!/usr/bin/python
#coding=utf-8
import codecs

from commands import getstatusoutput
def run_crf_plus():
    args = './crf_learn -t feature.txt corpus_transformed.txt model'
    status, output = getstatusoutput(args)
    start = 0
    lines = output.strip().split("\n")
    print 'the crf++ output:'
    for line in lines:
        if line == '':
            start += 1
        if start < 2:
            continue
        else:
            print line
def transfrom_model_file(modelname):
    print 'convert the data from crf++...'
    with codecs.open("model.txt",'r','utf-8') as f:
        input_data = f.readlines()
    with codecs.open("output/feature_dict.txt",'r','utf-8') as f:
        feature_dict = f.readlines()
    
    feature_line = 3
    value_line = 4
    start = 0
    feature_dict_tools = {}
    feature_value = []
    for line in input_data:
        if line == '\n':
            start+=1
            continue  
        if start == feature_line:
            words = line.strip().split()
            feature_dict_tools[words[1]] = words[0]
        if start == value_line:
            feature_value.append(float(line))
    s = 'BMES'
    model = codecs.open(modelname,'w','utf-8')
    for line in feature_dict:
        words = line.strip().split()
        if words[0] in feature_dict_tools:
            pos = int(feature_dict_tools[words[0]])
            coding = words[1]
            for i in range(4):
                tag_id = str(i)
                feature_id = str(words[1])
                feature_id_value = str(feature_value[pos+i])
                feature_str = tag_id+"_"+feature_id+"\t"+feature_id_value+"\n"
                model.write(feature_str)
    model.close()       
            
if __name__ == '__main__':
    #transfrom_model_file('output/mymodel.txt')
    run_crf_plus()
    transfrom_model_file('output/mymodel.txt')