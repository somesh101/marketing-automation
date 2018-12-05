#!/usr/bin/python
#retrieving information
import mysql.connector as mariadb
import os
import re

class Dealer:
    base=""
    filename1=''
    filename2=''
    outkeyfile=''
    outadfile=''
    directory=''
    mariadb_connection = None #mariadb.connect(user= "somesh",password="PbUsu3aV5I5rpsKOyeWU",host="  1.0.26.74",database="carsinfo")
    cursor = None #mariadb_connection.cursor(named_tuple=True, buffered=True)
    templatekey = []
    templatead = []

    def __init__(self):
        self.base=input("Enter path for template folder skip filename) : ")
        self.filename1=input("Enter key file name of Template : ")
        self.filename2=input("Enter ad file name of template : ")
        self.outkeyfile=input("Enter key file name for output : ")
        self.outadfile=input("Enter ad file name for output : ")
        self.directory=input("Enter output folder (for entire output) : ")
        self.mariadb_connection = mariadb.connect(user= "somesh",password="PbUsu3aV5I5rpsKOyeWU",host="  1.0.26.74",database="carsinfo")
        self.readTemplate()

    def __init__(self,base,filename1,filename2,outkeyfile,outadfile,directory):
        self.filename1 = filename1
        self.filename2 = filename2
        self.outkeyfile = outkeyfile
        self.outadfile = outadfile
        self.base=base
        self.directory=directory
        self.mariadb_connection = mariadb.connect(user= "somesh",password="PbUsu3aV5I5rpsKOyeWU",host="  1.0.26.74",database="carsinfo")
        self.readTemplate()

    def getOemNameFromDealers(self):
        query='''SELECT distinct oem_name
        FROM dealer_outlet do order by oem_name asc'''
        #[list of oem_names]
        self.cursor = self.mariadb_connection.cursor(named_tuple=True, buffered=True)

        oem_list=[]
        self.cursor.execute(query)
        for each in self.cursor:
            if each[0]!= None:
                oem_list.append(each[0])
        #return ['Hindustan Motors','Maruti']
        self.cursor.close()
        return list(filter(lambda a:(a!='' and a!=None),oem_list))

    def getCarForOem(self,oem_name):
        query='''SELECT oemname,carname
        FROM car WHERE (StartDate < CURDATE() AND EndDate > CURDATE()) AND oemname in {} GROUP BY 2 ORDER BY carname'''
        self.cursor = self.mariadb_connection.cursor(named_tuple=True, buffered=True)
        carname_dict={}
        oem_names=tuple(oem_name)
        self.cursor.execute(query.format(oem_names))
        for each in self.cursor:
            #{oem_name: list of carname, oem_name: list of carname.....}
            if each[0] not in carname_dict.keys():
                carname_dict[each[0]]=[each[1]]
            else :
                carname_dict[each[0]].append(each[1])
        print(carname_dict)
        self.cursor.close()
        return carname_dict

    def getCarInfo(self,oem_name):
        query='''SELECT oem_name,COUNT(do.id_dealer_outlet) as count,ci.CityName
        FROM dealer_outlet do
        LEFT JOIN address ad ON do.id_address = ad.id_address
        LEFT JOIN city ci ON ad.id_city = ci.CityId
        WHERE dealer_role = 2
        AND oem_name = '{}'
        AND end_date > NOW()
        GROUP BY 3
        ORDER BY oem_name ASC'''
        self.cursor = self.mariadb_connection.cursor(named_tuple=True, buffered=True)
        # {oem_name:[[dealer_count,city],[dealer_count,city]....}
        carinfo={oem_name:[]}
        self.cursor.execute(query.format(oem_name))
        for each in self.cursor:
            carinfo[each[0]].append([each[1],each[2]])
        self.cursor.close()
        return carinfo

    def readTemplate(self):
        try:
            fil = open(str(self.base+'/'+self.filename1),'r')
            print("Loading Key template....",end='')
            self.templatekey.append(fil.readline()) #= readTemplate(str(base+'/'+filename1))
            self.templatekey.append(fil.read())
            print('done')
            fil.close()

            fil = open(str(self.base+'/'+self.filename2),'r')
            print("Loading ad template....",end='')
            self.templatead.append(fil.readline()) #= readTemplate(str(base+'/'+filename1))
            self.templatead.append(fil.read())
            print('done')
            fil.close()

        except FileNotFoundError:
            print("Wrong File Name")
        except :
            print("Unkown Error Occured in reading template : "+filename)

    def populate(self,oem_name,carname):
        carname=set(carname)
        #{oem_name:[[dealer_count,city],[dealer_count,city]....}
        print("fetching dealer details ... ",end='')
        oem_carinfo_dict=self.getCarInfo(oem_name)
        print('done')
        if len(oem_carinfo_dict[oem_name])==0:
            print('No information for {}'.format(oem_name))
            return
        keyer=[]
        #pdb.set_trace()
        #create folder for oemname if not exist
        if not os.path.exists(str(self.directory+'/'+oem_name)):
            print("creating directory ",str(self.directory+"/"+oem_name))
            os.makedirs(str(self.directory+"/"+oem_name))
        print(carname)
        #for each model generate new template
        for eachcar in set(carname):
            writkey=None
            writad=None
            eachcar=re.sub('\d{4}-\d{4}','',eachcar)
            eachcar=re.sub(' +',' ',eachcar)
            if not os.path.exists(str(directory+"/"+oem_name+"/"+eachcar)):
                print("creating directory ",str(self.directory+"/"+oem_name+"/"+eachcar))
                os.makedirs(str(self.directory+"/"+oem_name+"/"+eachcar))
            writkey = open(str(self.directory+"/"+oem_name+"/"+eachcar+"/"+outkeyfile), 'a',newline='\n')
            writad = open(str(self.directory+"/"+oem_name+"/"+eachcar+"/"+outadfile), 'a',newline='\n')
            writkey.write(self.templatekey[0])
            writad.write(self.templatead[0])
            #Inner loop
            try:
                for eachcity in oem_carinfo_dict[oem_name]:
                    templatekeyTemp=self.templatekey[1]
                    templateadTemp=self.templatead[1]
                    try:
                        if oem_name in eachcar :
                            templatekeyTemp = re.sub('<[bB]rand [+]{0,1}<[Mm]odel>','<model>',templatekeyTemp)

                        templatekeyTemp=templatekeyTemp.replace('<brand>',oem_name)
                        templatekeyTemp=templatekeyTemp.replace('<model>',eachcar)
                        templatekeyTemp=templatekeyTemp.replace('<city>',eachcity[1])
                        #capials
                        templatekeyTemp=templatekeyTemp.replace('<Brand>',oem_name)
                        templatekeyTemp=templatekeyTemp.replace('<Model>',eachcar)
                        templatekeyTemp=templatekeyTemp.replace('<City>',eachcity[1])

                        #write adwrords
                        if oem_name in eachcar :
                            templateadTemp=templateadTemp.replace('<brand> <model>','<model>')
                            templateadTemp=re.sub('<[bB]rand [+]{0,1}<[Mm]odel>','<model>',templateadTemp)

                        templateadTemp=templateadTemp.replace('<brand>',oem_name)
                        templateadTemp=templateadTemp.replace('<model>',eachcar)
                        templateadTemp=templateadTemp.replace('<city>',eachcity[1])
                        templateadTemp=templateadTemp.replace('<count>',str(eachcity[0]))
                        #capitals
                        templateadTemp=templateadTemp.replace('<Brand>',oem_name)
                        templateadTemp=templateadTemp.replace('<Model>',eachcar)
                        templateadTemp=templateadTemp.replace('<City>',eachcity[1])
                        templateadTemp=templateadTemp.replace('<Count>',str(eachcity[0]))

                        writkey.write(templatekeyTemp)
                        writad.write(templateadTemp)
                    except KeyError:
                        keyer.append(eachcity)
                    except :
                        traceback.print_stack()
                        print("Unkwn error")
            except Exception as e:
                keyer.append(oem_name)
            try :
                writkey.close()
                writad.close()
            except :
                pass
        if len(keyer)>0:
            print("Keyerror")
            print(keyer)

    def driver(self):
        #----[list of oem_names]
        print("fetching oem names....",end='')
        oem_name_list=self.getOemNameFromDealers()
        print("done")
        print("fetching car names....",end='')
        #---{oem_name: list of carname, oem_name: list of carname.....}
        oem_carname_dict=self.getCarForOem(oem_name_list)
        print("done")
        #populate(oem_name,list of carname_dict,keyTemplate,adtemplate,cursor)
        for each in oem_carname_dict.keys():
            #print("Writing ",each," and  ",set(oem_carname_dict[each]))
            print(".... Please wait......")
            self.populate(each,oem_carname_dict[each])

    def __del__(self):
        try:
            self.cursor.close()
            self.mariadb_connection.close()
        except:
            continue
if __name__=='__main__':
    base="/home/somesh/Documents/raw_static/pythonModules"
    filename1='service_key.csv'
    filename2='service_ad.csv'
    outkeyfile='key.csv'
    outadfile='ad.csv'
    directory='/home/somesh/Documents/service-center'
    dealer = Dealer(base,filename1,filename2,outkeyfile,outadfile,directory)
    dealer.driver()
