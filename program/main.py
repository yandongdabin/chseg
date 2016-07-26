#coding=utf-8
#!/usr/bin/python
import sys,getopt
from  corpus_transform import *
from train_with_tool import *
from feature import *
from model_predict import *
from change_predict_file import *
command = {'t':4,'p':4}
class engine(object):
    def __init__(self):
       self.history_command = []
       self.cur_pos = 0
def usage():
    str = """
    --train -t template_file -i corpus_file\n
    --test -t template_file -i test_file\n
    -t specify the template file name. \n
    -i corpus file name for train model and test file for predict.\n
    """
    print str
if __name__=='__main__':
    try:
        opts, args = getopt.getopt(sys.argv[1:], "ht:i:",["train","test"])
    except Exception,e:
        print e
        sys.exit(-1)
    train_test = -1
    template_file = ''
    input_file = ''
    for op,value in opts:
        if op=='--train':
            train_test = 0
        elif op == '--test':
            train_test = 1
        elif op == '-t':
            template_file = value
        elif op == '-i':
            input_file = value
        elif op =='-h':
            usage()
            exit(0)
    if(train_test == 0 and input_file != '' and template_file != ''):
        character_tagging(input_file,'corpus_transformed.txt')
        res = read_feature_file(template_file)
        select_feature("corpus_transformed.txt","output/feature_learned.txt",res)
        character_tagging(input_file,'corpus_transformed.txt',False)
        run_crf_plus()
        transfrom_model_file("output/model.txt")
    elif(train_test == 1 and input_file != '' and template_file != ''): 
        a = model_pridict("output/model.txt","output/feature_dict.txt",template_file)
        change_predict_file(input_file,'changed_file.data')
        a.predict_file('changed_file.data') 
        calc_precision('result.txt','right.txt')
    else:
        usage()