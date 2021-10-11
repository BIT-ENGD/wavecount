import multiprocessing as mp
import os
import filetype as ft 
import shutil
import math 
import pickle as pk
am = __import__('audio-metrics')


#am.calmd5("/path/to/file")
SRC="/data/linux/1whr/"

BADFILES=[]
TARFILES=[]

DEBUG=False

TESTDIR="/data/wd1t/temp/"



PROCESS_NUM=32

RESULT_FILE="result_{}.dat"


def save_vars(var,filename):
    with open(filename,"wb") as f:
        pk.dump(var,f)


def load_vars(filename):
    with open(filename,"rb") as f:
        return pk.load(f)

def process_proc(filelist,SRCTAR,id):
    totaltime=0
    FILEPATH=[]
    BADFILE=[]
    RESULT={}
    for fullfile in filelist:
        status,duration,filepath=am.testfile(fullfile,SRCTAR)
        if(status):
            totaltime+=duration
            FILEPATH.append(fullfile)
        else:
            BADFILE.append(fullfile)
    
    RESULT["goodfile"]=FILEPATH
    RESULT["badfile"]=BADFILE
    RESULT["totaltime"]=totaltime
    filename=RESULT_FILE.format(id)
    save_vars(RESULT,filename)
    #print("totaltime:",totaltime)
       
    
def testdirwithmp(SRCDIR,SRCTAR):
    FILELIST=[]
    g=os.walk(SRCDIR)
    for path,dir_list,file_list  in g:
        for file in file_list:
            fullfile=path+os.sep+file
            FILELIST.append(fullfile)
    record=[]
    filenum=math.ceil(len(FILELIST)/PROCESS_NUM)
    for i in range(PROCESS_NUM):

        partfilelist=FILELIST[i*filenum:(i+1)*filenum]
        process = mp.Process(target=process_proc, args=(partfilelist, SRCTAR,i))
        process.start()
        record.append(process)

    for pitem in record:
        pitem.join()
     
    g=os.walk("./")
    RESULT={}
    RESULT["goodfile"]=[]
    RESULT["badfile"]=[]
    RESULT["totaltime"]=0
    for path,dir_list,file_list  in g:
        for file in file_list:
            if(os.path.splitext(file)[1][1:] == "dat"):
                fullfile=path+os.sep+file
                partret=load_vars(fullfile)
                RESULT["goodfile"].extend(partret["goodfile"])
                RESULT["badfile"].extend(partret["badfile"])
                RESULT["totaltime"]+=partret["totaltime"]
    
    print("[part]:","totaltime:",RESULT["totaltime"], RESULT["totaltime"]/3600," path:",SRCTAR)
    return RESULT


def dotestwithmp(SRC):
    BADFILES=[]
    RESULT={}
    RESULT["goodfile"]=[]
    RESULT["badfile"]=[]
    RESULT["totaltime"]=0
    g=os.walk(SRC)
    for path,dir_list,file_list  in g:
             
        for file in file_list:
            fullfile=os.path.join(path,file)
            
            fileinfo=ft.guess(fullfile)
            if(fileinfo == None):
                BADFILES.append(fullfile)
                continue
            if fileinfo.extension == "tar" :
                if not DEBUG and os.path.exists(TESTDIR):
                    shutil.rmtree(TESTDIR) 
                    os.mkdir(TESTDIR)

                print("-"*30,"processing file: ",fullfile,"-"*30)
                if not DEBUG:
                    am.untar(fullfile,TESTDIR)
                TARRESULT=testdirwithmp(TESTDIR,fullfile)
                RESULT["goodfile"].extend(TARRESULT["goodfile"])
                RESULT["badfile"].extend(TARRESULT["badfile"])
                RESULT["totaltime"]+=TARRESULT["totaltime"]

                TARFILES.append(fullfile)
            elif( fileinfo.extension == "wav"):
                status,duration,filepath=am.testfile(fullfile,"")
                if(status):
                    RESULT["totaltime"]+=duration
                    RESULT["goodfile"].extend(filepath)
                else:
                    RESULT["badfile"].extend(filepath)
                
            else:
                BADFILES.append(fullfile)

    print("totaltime:",RESULT["totaltime"],"(Seconds) ", RESULT["totaltime"]/3600," (hours)")
    print("badfile:",BADFILES)
    

    save_vars(RESULT,"final_result.dat")

if __name__== "__main__":
    
    DEBUG=False 
    dotestwithmp(SRC)