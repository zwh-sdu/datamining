# -*- coding: utf-8 -*-
"""
Created on Wed Sep 29 14:47:57 2021

@author: 张文浩
"""

#导入相关库
import sys
import math
from collections import defaultdict
from functools import reduce  
from textblob import TextBlob        #导入文本处理工具
from textblob import Word
import json

Wt_d = defaultdict(dict) #记录Wt,d
doc_score = defaultdict(dict) #记录每个doc的最终得分
doc_tot = 0#总共有多少个文件
doc_num=defaultdict(int)#文档
Wt_q=defaultdict(int)#词数
df0 = defaultdict(dict)
smart=""

#为提前获得df而先读一遍文件的函数
def get_df():
    global doc_tot
    f = open(r"E:\datamining\exp1\tweets.txt")
    lines = f.readlines()
    uselessword = [",","'","‘","“","’","-","”","——"]
    #一行一行处理
    for line in lines:
        doc_tot += 1
        #大写转小写
        line = line.lower()
        line = json.loads(line)
        #处理当前行得到tweetidid和text文本
        tweetid = Word(line['tweetid'])
        text = TextBlob(line['text']+" "+line['username']).words.singularize()
        texts = []
        for word in text:
            if word in uselessword:
                continue
            temp = Word(word)
            temp = temp.lemmatize("v") #词形还原
            texts.append(temp)
        
        unique_terms=set(texts)
        for term in unique_terms:
            df0[term][tweetid]=1

def compute_Wt_d():
    global Wt_d
    #读入数据
    f = open(r"E:\datamining\exp1\tweets.txt")
    lines = f.readlines()
    uselessword = [",","'","‘","“","’","-","”","——"]
    #一行一行处理
    for line in lines:
        #大写转小写
        line = line.lower()
        line = json.loads(line)
        #处理当前行得到tweetidid和text文本
        tweetid = Word(line['tweetid'])
        text = TextBlob(line['text']+" "+line['username']).words.singularize()
        texts = []
        for word in text:
            if word in uselessword:
                continue
            temp = Word(word)
            temp = temp.lemmatize("v") #词形还原
            texts.append(temp)
        doc_num={} #记录这个词出现的次数
        for term in texts:
            if term in doc_num.keys():
                doc_num[term]+=1
            else:
                doc_num[term]=1
        #n/l/a/b/L
        if(smart[0]=='n'):
            pass
        if(smart[0]=='l'):
            for term in doc_num.keys():
                doc_num[term]=math.log(doc_num[term])+1
        if(smart[0]=='a'):
            maxx=0
            for term in doc_num.keys():
                if maxx<doc_num[term]:
                    maxx=doc_num[term]
            for term in doc_num.keys():
                doc_num[term]=0.5+(0.5*doc_num[term])/maxx
        if(smart[0]=='b'):
            for term in doc_num.keys():
                doc_num[term]=1
        if(smart[0]=='L'):
            ave=0;
            for term in doc_num.keys():
                ave+=doc_num[term]
            ave/=len(doc_num)
            for term in doc_num.keys():
                doc_num[term]=(1+math.log(doc_num[term]))/(1+math.log(ave))
                
        #n/t/p
        if(smart[1]=='n'):
            pass
        if(smart[1]=='t'):
            for term in doc_num.keys():
                doc_num[term]*=math.log(doc_tot/len(df0[term]))
        if(smart[1]=='p'):
            for term in doc_num.keys():
                doc_num[term]*=max(0,math.log((doc_tot-len(df0[term]))/len(df0[term])))
        
        #归一化
        #n/c
        if(smart[2]=='n'):
            pass
        if(smart[2]=='c'):
            sum=0
            for term in doc_num.keys():
                sum=sum+doc_num[term]*doc_num[term]
            sum=1.0/math.sqrt(sum)
            for term in doc_num.keys():
                doc_num[term]=doc_num[term]*sum
            
        unique_terms=set(texts)
        for term in unique_terms:
            Wt_d[term][tweetid]=doc_num[term]         

def compute_score(query):
    global doc_score,Wt_q
    doc_score={}
    Wt_q={}
    for term in query:
        if term in Wt_q:
            Wt_q[term]+=1
        else:
            Wt_q[term]=1
    
    #n/l/a/b/L
    if(smart[4]=='n'):
        pass
    if(smart[4]=='l'):
        for term in Wt_q.keys():
            Wt_q[term]=math.log(Wt_q[term])+1
    if(smart[4]=='a'):
        maxx=0
        for term in Wt_q.keys():
            if maxx<Wt_q[term]:
                maxx=Wt_q[term]
        for term in Wt_q.keys():
            Wt_q[term]=0.5+(0.5*Wt_q[term])/maxx
    if(smart[4]=='b'):
        for term in Wt_q.keys():
            Wt_q[term]=1
    if(smart[4]=='L'):
        ave=0;
        for term in Wt_q.keys():
            ave+=Wt_q[term]
        ave/=len(Wt_q)
        for term in Wt_q.keys():
            Wt_q[term]=(1+math.log(Wt_q[term]))/(1+math.log(ave))
    
    #n/t/p
    if(smart[5]=='n'):
        pass
    if(smart[5]=='t'):
        for term in Wt_q.keys():
            Wt_q[term]*=math.log(doc_tot/len(df0[term]))
    if(smart[5]=='p'):
        for term in Wt_q.keys():
            Wt_q[term]*=max(0,math.log((doc_tot-len(df0[term]))/len(df0[term])))
            
    #归一化
    #n/c
    if(smart[6]=='n'):
        pass
    if(smart[6]=='c'):
        sum=0
        for term in Wt_q.keys():
            sum=sum+Wt_q[term]*Wt_q[term]
        sum=1.0/math.sqrt(sum)
        for term in Wt_q.keys():
            Wt_q[term]=Wt_q[term]*sum
        
#    for term in Wt_q.keys():
#        if term in Wt_d:
#            df=len(Wt_d[term])
#        else:
#            df=doc_tot
#        Wt_q[term]=(math.log(Wt_q[term])+1)*math.log(doc_tot/df)
            
    for term in query:
        if term in Wt_d:
            for doc in Wt_d[term]:
                if doc in doc_score.keys():
                    doc_score[doc]+=Wt_d[term][doc]*Wt_q[term]
                else:
                    doc_score[doc]=Wt_d[term][doc]*Wt_q[term]
    doc_score_sorted=sorted(doc_score.items(),key=lambda x:x[1],reverse=True)
    return doc_score_sorted

def myinput(doc):
    #处理手动输入的数据，方便与terms中的存好的term进行匹配
    doc = doc.lower()
    terms = TextBlob(doc).words.singularize()
    res = []
    for term in terms:
        term = Word(term)
        term = term.lemmatize("v") #词形还原
        res.append(term)
    return res

#取并集函数
def Union(sets):
    return reduce(set.union, [s for s in sets])

def search():       #查询
    n=int(input("请输入想得到的最相关的doc的数量：  "))
    if (n==0):
        sys.exit()
    query = myinput(input("请输入要查询词,退出请键入exit： "))
    ans = []
    if len(query)==0:
        sys.exit()
    ans_num = Union([set(Wt_d[term].keys()) for term in query])
    print("一共有"+str(len(ans_num))+"条相关doc")
    print("与输入相关性最大的"+str(n)+"个doc的score及其tweetid分别是:")#调用sorted函数对score进行排序
    scores=compute_score(query)
    i = 1
    for (id, score) in scores:
        if i<=n:#返回前n条查询到的信息
            ans.append(id)
            print(str(score) + ": " + id)
            i = i + 1
        else:
            break
    
def main():
    global smart
    get_df()
    smart=input("请输入计算机制，格式请标准如：lnc.ltn: ")
    compute_Wt_d()
    while 1:
        search()
        
        
if __name__ == "__main__":
    main()