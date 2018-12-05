import csv
import sys
import ast
import re
import os
import requests
not_found_url=0
total_url=0
def bestfit(inp,lenth,unique):
    i = len(inp)-lenth
    best=''
    if(i>0):
        for u in sorted(unique.keys(),key=len):
            if u in inp and len(u)>=i:
                best=u
    return best

def replac(inp,lenth,file_name):
    try :
        with open(file_name) as file:
            #print("loading : ",file_name )
            unique=ast.literal_eval(file.read())
    except :
        print("Warnng : {} Dictionary Empty".format(file_name))
        unique={}

    #print(unique)
    while(len(inp)>lenth):
        best = bestfit(inp,lenth,unique)
        if(best!=''):
            inp=inp.replace(best,unique[best])
        else :
            print(lenth," : ",len(inp)," : ",inp)
            print("\n Enter new key pair for replacement : ")
            key = input("key : ")
            value = input("value : ")
            unique[key]=value
            #print(unique)
            with open(file_name,'w') as file:
                print("Updating : ",file_name )
                file.write(str(unique))
    return inp
#fileName = input("Enter location (/..../) ")

def urlVerify(Url):
    global total_url
    global not_found_url
    total_url+=1
    return Url[:-4]
    c=requests.head(Url)
    if(c.status_code==200):
        return Url
    elif Url[-4:]=='.htm':
        c=requests.get(Url[:-4])
        if c.status_code==200:
            return Url[:-4]
    else :
        c=requests.get(str(Url+'.htm'))
        if c.status_code==200:
            return str(Url+'.htm')

    print("*** WARNING ***** ")
    print("link doesn't exist : ",Url)
    not_found_url+=1
    return Url

def loader(path):
    #>>> spamReader = csv.reader(open('eggs.csv', newline=''), delimiter=' ', quotechar='|')
    #print(path)
    csvReader = csv.DictReader(open(path,'r'))
    filedNames=list(csvReader.fieldnames)
    csvwriter = csv.DictWriter(open(str(path[:-4]+"_modified.csv"),'w',newline='\n'),fieldnames=filedNames)
    csvwriter.writeheader()
    for row in csvReader:
        #Headline 1	Headline 2	Description	Path 1	Path 2	Final URL
        row['Headline 1']= replac(row['Headline 1'],30,'uniqueH1')
        row['Headline 2']= replac(row['Headline 2'],30,'uniqueH2')
        row['Description']= replac(row['Description'],90,'uniqueD1')
        row['Path 1']= replac(row['Path 1'],15,'uniqueP1')
        row['Path 2']= 'Service Center'
        row['Final URL']= urlVerify(row['Final URL'])
        csvwriter.writerow(row)


def keyreplace(path):
    #>>> spamReader = csv.reader(open('eggs.csv', newline=''), delimiter=' ', quotechar='|')
    csvReader = csv.reader(open(path),delimiter=",",quotechar="\"")
    csvwriter = csv.writer(open(str(path[:-4]+"_modified.csv"),'w',newline='\n'),delimiter=",",quotechar="\"")
    for row in csvReader:
        if(row[3]=="Broad"):
            inp2 = re.split('\W+',row[2])
            inp3list=[]
            for each in inp2:
                if each not in inp3list:
                    inp3list.append(each)
            row[2]= ' + '.join(inp3list)
        if row[3]=="Exact":
            inp2 = re.split('\W+',row[2][1:-1])
            inp3list=[]
            for each in inp2:
                if each not in inp3list:
                    inp3list.append(each)
            row[2]= str('['+' '.join(inp3list)+']')
        csvwriter.writerow(row)


def explorer(path):
    print(path)
    filename=os.listdir(path)
    for each in filename:
        if(os.path.isdir(str(path+'/'+each))):
            explorer(str(path+'/'+each))
        else:
            if 'key' in each :
                keyreplace(str(path+'/'+each))
            if 'ad' in each:
                loader(str(path+'/'+each))

if __name__ == "__main__":
    dir="/home/somesh/Documents/service-center/"
    explorer(dir)
    print("Total Url found : ",total_url)
    print("URL not found : ",not_found_url)
