
from scrapy import Selector
from tqdm import tqdm
import requests
import math
import re
import sqlite3
import subprocess
import sys,os
import tempfile
import xml.etree.ElementTree as ET
import time
import signal
signal.signal(signal.SIGINT, lambda x,y: sys.exit(0))
#Global Variables

conn = sqlite3.connect('MSPatch.db')
c=conn.cursor()
cabname=[]
extractedcabs=[]
rangestart=[]
updatetempfiles_path= tempfile.gettempdir()+"\\winupdate"
patches=[]
programs=[]
final_updates_list=[]
solved_revisionids=[]

#Functions

def concatenate_list_data(list):
    result= ''
    for element in list:
        result += str(element)
    return result

def parse_wssuscn2cab(buff):
	global cabname,rangestart,extractedcabs
	scrape=Selector(text=buff)
	updateid=scrape.xpath("//update/@updateid").extract_first()
	
	if c.execute("select updateid from MSPatchTable where updateid=\""+updateid+"\"").fetchall().__len__()>0:
		return
	creationdate=scrape.xpath("//update/@creationdate").extract_first()
	revisionid=scrape.xpath("//update/@revisionid").extract_first()
	cabtoextract=""
	for i in range(cabname.__len__()-1):

		if int(revisionid)>int(rangestart[i]):
			pass
		else:
			cabtoextract=cabname[i]
			break
	if cabtoextract=="":
		cabtoextract=cabname[cabname.__len__()-1]
	
	if cabtoextract in extractedcabs:
		pass
	else:
		for f in os.listdir(updatetempfiles_path):
			if os.path.isdir(updatetempfiles_path+"\\"+f):
				os.system("rmdir "+updatetempfiles_path+"\\"+f+" /S /Q")
		mute=subprocess.check_output(".\\7z.exe x "+updatetempfiles_path+"\\wsusscn2.cab "+cabtoextract+" -o"+updatetempfiles_path+" -y")
		mute=subprocess.check_output(".\\7z.exe x "+updatetempfiles_path+"\\"+cabtoextract+" -o"+updatetempfiles_path+" -y")
		os.system("del "+updatetempfiles_path+"\\"+cabtoextract)
		extractedcabs.append(cabtoextract)
	
	prerequisite=list_to_string(scrape.xpath("//prerequisites/*/@id").extract())
	supersededby=list_to_string(scrape.xpath("//supersededby/*/@id").extract())
	if  scrape.xpath("//category[@type = 'Company']/@id").extract_first():
		Category_Company =  list_to_string(scrape.xpath("//category[@type = 'Company']/@id").extract_first())
		Category_Product= list_to_string(scrape.xpath("//category[@type = 'Product']/@id").extract())
		Category_ProductFamily=list_to_string(scrape.xpath("//category[@type = 'ProductFamily']/@id").extract())
		Category_UpdateClassification=list_to_string(scrape.xpath("//category[@type = 'UpdateClassification']/@id").extract())
		
		
	else:
		Category_Company=Category_Product=Category_ProductFamily=Category_UpdateClassification=prerequisites=""

	try:
		scrape=Selector(text=(re.sub(r'[^\x00-\x7f]','',concatenate_list_data(open(updatetempfiles_path+"\\c\\"+revisionid,"r").readlines()).replace("\n","").replace("\r","").replace("\t","").strip(" "))))
		supersedes=list_to_string(scrape.xpath("//supersededupdates/updateidentity/@updateid").extract())
	except Exception as e:
		supersedes=""
	
	try:
		scrape=Selector(text=(re.sub(r'[^\x00-\x7f]','',concatenate_list_data(open(updatetempfiles_path+"\\l\\en\\"+revisionid,"r").readlines()).replace("\n","").replace("\r","").replace("\t","").strip(" "))))
		title=re.sub(r'[^\x00-\x7f]','',str(scrape.xpath("//title/text()").extract_first()))
		description=re.sub(r'[^\x00-\x7f]','',str(scrape.xpath("//description/text()").extract_first()))
	except Exception as e:
		title=""
		description=""
	try:
		scrape=Selector(text=(re.sub(r'[^\x00-\x7f]','',concatenate_list_data(open(updatetempfiles_path+"\\s\\"+revisionid,"r").readlines()).replace("\n","").replace("\r","").replace("\t","").strip(" "))))
		msrcseverity=str(scrape.xpath("//properties/@msrcseverity").extract_first())
		msrcnumber=str(scrape.xpath("//securitybulletinid/text()").extract_first())
		kb="KB"+str(scrape.xpath("//properties/kbarticleid/text()").extract_first())
		languages=list_to_string(scrape.xpath("//properties/language/text()").extract())
		
	except Exception as e:
		msrcnumber=""
		msrcseverity=""
		kb=""
		languages=""
		
	try:
		scrape=Selector(text=(re.sub(r'[^\x00-\x7f]','',concatenate_list_data(open(updatetempfiles_path+"\\x\\"+revisionid,"r").readlines()).replace("\n","").replace("\r","").replace("\t","").strip(" "))))
		category=str(scrape.xpath("//categoryinformation/@categorytype").get())
	except Exception as e:
		category=""
	
	try:	
		params=(updateid,revisionid,creationdate,Category_Company,Category_Product,Category_ProductFamily,Category_UpdateClassification,prerequisite,title,description,msrcseverity,msrcnumber,kb,languages,category,supersededby,supersedes)
		c.execute('Insert into MSPatchTable values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',params) 
	except Exception as e:
		pass
	
def download_cab():
	print "\n\nThis is going to take some time. Please be patient .... \n\nGrabbing a cup of coffee might be a good idea right now !! :P \n\nStep 1 out of 4 :- Downloading Official WSUS Update Cab File\n\n"
	url="http://go.microsoft.com/fwlink/?linkid=74689"
	r=requests.get(url, stream=True)
	total_size = int(r.headers.get('content-length', 0)); 
	block_size = 1024
	wrote = 0 
	if os.path.isdir(updatetempfiles_path):
		pass
	else:
		mute=subprocess.check_output("mkdir "+updatetempfiles_path)
		
	with open(updatetempfiles_path+'\\wsusscn2.cab', 'wb') as f:
		for data in tqdm(r.iter_content(block_size), total=math.ceil(total_size//block_size) , unit='KB', unit_scale=True):
			wrote = wrote  + len(data)
			f.write(data)
	if total_size != 0 and wrote != total_size:
		print("ERROR, something went wrong")
		sys.exit()

def list_to_string(buff):
	return str(buff).replace("u'","").replace("[","").replace("]","").replace("'","").replace("\r","").replace("\n","")
	
def solve_supersede_updateids(applicable_updates):
	global final_updates_list
	superseded_updates=[]
	applicable_updates_query=str(applicable_updates).replace("u'","'").replace("[","(").replace("]",")")
	record=c.execute("select supersededby from MSPatchTable where updateid in "+applicable_updates_query+";")
	for i,j in zip(record.fetchall(),range(0,applicable_updates.__len__())):
		if i[0].__len__()==0:
			final_updates_list.append(applicable_updates[j])
			record=c.execute("select revisionid from MSPatchTable where updateid ='"+applicable_updates[j]+"';")
			solved_revisionids.append(record.fetchall()[0][0])
		else:
			solve_supersede_revisionids(i[0])
	
def solve_supersede_revisionids(revisionids):
	for i in revisionids.split(","):
		if i.strip(" ") in solved_revisionids:
			continue
		record=c.execute("select updateid,supersededby from MSPatchTable where revisionid='"+i.strip(" ")+"' ;")
		for j in record.fetchall():
			if j[1].__len__()==0:
				if j[0] in final_updates_list:
					continue
				else:
					final_updates_list.append(j[0])
					solved_revisionids.append(i.strip(" "))
			else:
				solve_supersede_revisionids(j[1])
				solved_revisionids.append(i.strip(" "))
			
def update():
	global cabname,rangestart,i
	print_ascii_art()
	record=c.execute("SELECT count(name) FROM sqlite_master WHERE type='table' AND name='MSPatchTable';")
	if record.fetchone()[0] == 0:
		c.execute("""CREATE TABLE `MSPatchTable` (
	`updateid`	TEXT NOT NULL UNIQUE,
	`revisionid`	TEXT UNIQUE,
	`creationdate`	TEXT NOT NULL,
	`company`	TEXT,
	`product`	TEXT,
	`productfamily`	TEXT,
	`updateclassification`	TEXT,
	`prerequisite`	TEXT,
	`title`	TEXT,
	`description`	TEXT,
	`msrcseverity`	TEXT,
	`msrcnumber`	TEXT,
	`kb`	TEXT,
	`languages`	TEXT,
	`category`	TEXT,
	`supersededby`	TEXT,
	`supersedes`	TEXT,
	PRIMARY KEY(`updateid`)
);""")
		

		
	download_cab()
	print "\n\nStep 2 out of 4 :- Reading data from cab file and feeding the database\n\n"
	mute=subprocess.check_output(".\\7z.exe x "+updatetempfiles_path+"\\wsusscn2.cab index.xml -o"+updatetempfiles_path+" -y")
	mute=subprocess.check_output(".\\7z.exe x "+updatetempfiles_path+"\\wsusscn2.cab package.cab -o"+updatetempfiles_path+" -y")
	mute=subprocess.check_output(".\\7z.exe x "+updatetempfiles_path+"\\package.cab package.xml -o"+updatetempfiles_path+" -y")
	os.system("del \""+updatetempfiles_path+"\\package.cab\"")
	indexfile=open(updatetempfiles_path+"\\index.xml","r")
	indexf=indexfile.readlines()[0]
	scrape=Selector(text=indexf)
	cabname=scrape.xpath("//cab/@name").extract()
	rangestart=scrape.xpath("//cab/@rangestart").extract()
	indexfile.close()
	
	context = ET.iterparse(updatetempfiles_path+'\\package.xml', events=('end',))
	
	#Counting the number of tags to process for our status bar for Step 2
	i=0
	for event,elem in context:
		i+=1
	
	context = ET.iterparse(updatetempfiles_path+'\\package.xml', events=('end',))
	for event, elem in tqdm(context,total=i):
		if elem.tag == '{http://schemas.microsoft.com/msus/2004/02/OfflineSync}Update':
			parse_wssuscn2cab(ET.tostring(elem).replace("ns0:",""))
	print "\n\nStep 3 out of 4 :- Clearing temp cache \n\n"
	os.system("rmdir "+updatetempfiles_path+" /s /Q")
	print "Update Complete .....!! :) "
	conn.commit()
	print "\n\nStep 4 out of 4 :- Exporting the database as csv \n\n"
	exportdb("MSPatches.csv")

def scan(input_file):
	print_ascii_art()
	files=open(input_file,"r")
	a=str(files.readlines()).replace("\\n","")
	print str(a.replace("]","").replace("[","").replace("'","").replace(" ","").split(",").__len__())+" selected updates"
	solve_supersede_updateids(a.replace("]","").replace("[","").replace("'","").replace(" ","").split(","))
	print str(final_updates_list.__len__())+" applicable updates after solving for supersedes !!"

def exportdb(output_file):
	print_ascii_art()
	fileout=open(output_file,"w")
	fileout.write('"Update ID","Creation Date","Update Classification","Title","Description","KB ID","MSRC Severity","MSRC Number"\n')
	record=c.execute("select updateid,creationdate,updateclassification,title,description,kb,msrcseverity,msrcnumber from MSPatchTable where updateclassification not in ('','None') order by creationdate desc;")
	for i in tqdm(record.fetchall(),total=c.execute("select count(updateid) from MSPatchTable where updateclassification not in ('','None');").fetchone()[0]):
		updateclassification=c.execute("select title from MSPatchTable where updateid='"+i[2]+"';").fetchone()[0]
		fileout.write("\""+i[0]+"\",\""+i[1]+"\",\""+updateclassification+"\",\""+i[3]+"\",\""+i[4]+"\",\""+i[5]+"\",\""+i[6]+"\",\""+i[7]+"\""+"\n")
	fileout.close()
	print "\n \n DB Exported as CSV sucessfully !!"

def print_ascii_art():
	
	print r"""
	
      db         db
    d88           88
   888            888
  d88             888b        The HOLY ***
  888             d88P
  Y888b  /``````\8888
,----Y888        Y88P`````\
|        ,'`\_/``\ |,,    |
 \,,,,-| | o | o / |  ```'
       |  ''' '''  |
      /             \
     |               \
     |  ,,,,----'''```|
     |``   @    @     |
      \,,    ___    ,,/
         \__|   |__/
            | | |
            \_|_/
					
					
				CUW Tool - (C)heck for (U)pdates for (W)indows 
				By R4m
	"""

def help():
	print_ascii_art()
	
	print r"""Usage:-

	cuw.exe scan <filename with updateids> - Checks for Update ids in the input file and gives the final list of applicable updates with details 
	cuw.exe scan <filename with updateids> output <output file name> - Same as the previous option with the output (with extra details) being exported as csv 
	cuw.exe update - Updates the local patch database (Requires Internet Connection and some patience !! :P)
	cuw.exe exportdb <filename of the exported csv>" - Exports the local patch database as csv file
	cuw.exe help  -  Displays this help"""

def export(output_file):
	fileout=open(output_file,"w")
	finalupdates_query=str(final_updates_list).replace("u'","'").replace("[","(").replace("]",")")
	fileout.write('"Update ID","Creation Date","Update Classification","Title","Description","KB ID","MSRC Severity","MSRC Number"\n')
	record=c.execute("select updateid,creationdate,updateclassification,title,description,kb,msrcseverity,msrcnumber from MSPatchTable where updateid in "+finalupdates_query+" order by creationdate desc;")
	for i in tqdm(record.fetchall(),total=final_updates_list.__len__()):
		updateclassification=c.execute("select title from MSPatchTable where updateid='"+i[2]+"';").fetchone()[0]
		fileout.write("\""+i[0]+"\",\""+i[1]+"\",\""+updateclassification+"\",\""+i[3]+"\",\""+i[4]+"\",\""+i[5]+"\",\""+i[6]+"\",\""+i[7]+"\""+"\n")
	fileout.close()
	print "\n\n Report exported Successfully !!"

if os.path.isfile("7z.exe") and os.path.isfile("7z.dll"):
	pass
else:
	print_ascii_art()
	print "7z.exe or/and 7z.dll file not found in the current directory.\n\nCUW cannot function without these dependencies.\n\nPlease download the 7z binaries for your architecture (x86 / x64) and extract the mentioned files in the current directory and run the tool. Link :https://www.7-zip.org/download.html"
	sys.exit(1)
if sys.argv.__len__()==1:
	help()
elif sys.argv.__len__()==2:
	if sys.argv[1] == "update":
		update()
	else:
		help()
elif sys.argv.__len__() ==3:
	if sys.argv[1]== "scan":
		if os.path.isfile(sys.argv[2]):
			scan(sys.argv[2])
			records=c.execute("select title,kb from MSPatchTable where updateid in "+str(final_updates_list).replace("u'","'").replace("[","(").replace("]",")")+";")
			for i in records:
				print i[0]+" : "+i[1]
		else:
			print "\n\n"+sys.argv[2]+" file does not exist !!"
			help()
	elif sys.argv[1] == "exportdb":
		exportdb(sys.argv[2])
	else:
		help()
elif sys.argv.__len__()==5:
	if sys.argv[1]== "scan" and os.path.isfile(sys.argv[2]) and sys.argv[3] == "output":
		scan(sys.argv[2])
		export(sys.argv[3])
	else:
		help()
else:
	help()
	