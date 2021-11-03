# -*- coding: utf-8 -*-
"""
Created on Wed Sep 15 15:48:45 2021

@author: 张文浩
"""

#导入相关库
import sys
from collections import defaultdict
from textblob import TextBlob        #导入文本处理工具
from textblob import Word
import json

postings = defaultdict(dict) #inverted index

#处理整个文本的函数
def deal_postings():
    global postings
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
        #构建postings表
        #print(texts)
        tempset = set(texts)
        for term in tempset:
            if term in postings.keys():
                postings[term].append(tweetid)
            else:
                postings[term]=[tweetid]
    #建立完postings后要进行排序，方便后面优化查询，提高效率
    for term in postings.keys():
        postings[term].sort()

def oneword(a):
    global postings
    return postings[a]
    

def myand(a1,a2):
    global postings       #全局变量
    res = []
    if(a1 not in postings) or (a2 not in postings):
        return res
    else:
        #计算a1，a2对应postings数组的长度
        len1 = len(postings[a1]) 
        len2 = len(postings[a2])
        x=0
        y=0
        #双指针算法
        while x<len1 and y<len2:
            if postings[a1][x]==postings[a2][y]:
                res.append(postings[a1][x])
                x += 1
                y += 1
            elif postings[a1][x]<postings[a2][y]:
                x += 1
            else:
                y += 1
        return res

def myor(a1,a2):     #或操作
    res = []
    if(a1 not in postings) and (a2 not in postings):
        return res
    elif a2 not in postings:
        res = postings[a1]
    elif a1 not in postings:
        res = postings[a2]
    else:   #a1,a2都存在
        len1 = len(postings[a1]) 
        len2 = len(postings[a2])
        x=0
        y=0
        #同样采用双指针
        while x<len1 and y<len2:
            if postings[a1][x]==postings[a2][y]:
                res.append(postings[a1][x])
                x += 1
                y += 1
            elif postings[a1][x]<postings[a2][y]:
                res.append(postings[a1][x])
                x += 1
            else:
                res.append(postings[a2][y])
                y += 1
        if (x < len1):
            while( x<len1 ):
                res.append(postings[a1][x])
                x += 1
        if (y < len2):
            while( y<len2 ):
                res.append(postings[a2][y])
                y += 1
    return res

def mynot(a1,a2):      #非操作
    res = []
    if a1 not in postings:
        return res
    elif a2 not in postings:
        res = postings[a1]
        return res
    else:
        len1 = len(postings[a1]) 
        len2 = len(postings[a2])
        x=0
        y=0
        #双指针
        while x<len1 and y<len2:
            if postings[a1][x] == postings[a2][y]:
                x += 1
                y += 1
            elif postings[a1][x]<postings[a2][y]:
                res.append(postings[a1][x])
                x += 1
            else:
                y += 1
        if(x < len1):
            while( x<len1 ):
                res.append(postings[a1][x])
                x += 1
    return res
        

#def rank(terms):      #倒排索引
#    res = defaultdict(dict)
#    #res字典存每个doc出现的次数
#    for term in terms:
#        if term in postings:
#            for tweetid in postings[term]:
#                if tweetid in res:
#                    res[tweetid] += 1
#                else:
#                    res[tweetid] = 1
#    res = sorted(res.items(),key=lambda asd: asd[1],reverse=True)
#    return res

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

def inter(a1,a2):
    res = []
    if(len(a1) == 0) or (len(a2) == 0):
        return res
    else:
        #计算a1，a2对应postings数组的长度
        len1 = len(a1) 
        len2 = len(a2)
        x=0
        y=0
        #双指针算法
        while x<len1 and y<len2:
            if a1[x]==a2[y]:
                res.append(a1[x])
                x += 1
                y += 1
            elif a1[x]<a2[y]:
                x += 1
            else:
                y += 1
        return res 

def intersect(query):
    global postings
    #按照出现频率排序，查询优化
    query = sorted(query,key=lambda x:len(postings[x]))
    res = postings[query[0]]
    for i in range(len(query)):
        res = inter(res,postings[query[i]])
    return res

def search():       #查询
    query = myinput(input("请输入要查询词,退出请键入exit： "))
    if (query[0] == "exit") or (query == []):
        sys.exit()
    if (len(query) == 3 and (query[1]=="and" or query[1]=="or" or query[1]=="not")):
        if query[1] == "and":
            answer = myand(query[0],query[2])
            print("数量为 ")
            print(len(answer))
            print(answer)
        elif query[1] == "or":
            answer = myor(query[0],query[2])
            print("数量为 ")
            print(len(answer))
            print(answer)
        elif query[1] == "not":
            answer = mynot(query[0],query[2])
            print("数量为 ")
            print(len(answer))
            print(answer)
    elif len(query) == 1:
        answer = oneword(query[0])
        print("数量为 ")
        print(len(answer))
        print(answer)
    else:
        answer = intersect(query)
        print("and优化查询")
        print("数量为 ")
        print(len(answer))
        print(answer)
#        length = len(query)
#        rankdic = rank(query)
#        print("[Rank_Score: Tweetid]")
#        for(tweetid,score) in rankdic:
#            print(str(score/length)+ ": " + tweetid)

def main():
    deal_postings()
    while 1:
        search()
        
        
if __name__ == "__main__":
    main()


