import wave 
import os,tarfile
import shutil
import filetype as ft
import hashlib
import pyaudio,wave
# apt install portaudio19-dev
# pip install pyaudio
SRCPATH="/data/linux/1whr/" #500.chinese.wav"

TESTDIR="/data/wd1t/temp/"



FILEMD5=[]  #重复文件检测
BADFILES=[]  #坏文件检测
GOODFILES=[]
TOTALTIME=0
UNITIME=0
TARFILES=0

def calmd5(srcfile):
    with open(srcfile, 'rb') as fp:
        data = fp.read()
        file_md5= hashlib.md5(data).hexdigest()
        return file_md5
    return ""

def untar(fname, dirs):
    """
    解压tar.gz文件
    :param fname: 压缩文件名
    :param dirs: 解压后的存放路径
    :return: bool
    """
    try:
        t = tarfile.open(fname)
        t.extractall(path = dirs)
        return True
    except Exception as e:
        print(e)
        return False



def testfile(filepath,srctar):
    global TOTALTIME
    global FILEMD5
    global UNITIME
    bUniq=False
    if os.path.exists(filepath):
        filemd5=calmd5(filepath)
        if(filemd5 not in FILEMD5):
            bUniq=True
        FILEMD5.append(filemd5)

    fullfile=filepath
    info=os.path.split(fullfile)
    try:
        f=wave.open(fullfile)

        #playwave(fullfile,True)
    except:
        if(srctar == ""):              
            BADFILES.append(filepath)
        else:
            BADFILES.append(srctar+":"+info[1])
   
        return False,0,fullfile
    rate=f.getframerate()
    frames=f.getnframes()
    duration=frames/float(rate)
    #print("file {}, time: {} (s)".format(fullfile,duration))

    TOTALTIME+=duration
    if(bUniq):
        UNITIME+=duration

    if(srctar == ""):              
        GOODFILES.append(filepath)
    else:
        GOODFILES.append(srctar+":"+info[1])
   
                

    return True,duration,fullfile


def testdir(SRCDIR,SRCTAR):
   
    g=os.walk(SRCDIR)
    for path,dir_list,file_list  in g:
        for file in file_list:
            fullfile=path+os.sep+file
            status,duration,filepath=testfile(fullfile,SRCTAR)


def playwave(srcfile,output):
    beisu=1
    f=wave.open(srcfile,"rb")
    nc,sa,fr,nf=f.getparams()[:4]
    fr=int(fr*beisu)
    data=f.readframes(nf)
    p=pyaudio.PyAudio()
    s=p.open(format=p.get_format_from_width(sa),channels=nc,rate=fr,output=output)
    s.write(data)


def dotest(SRC):
    global BADFILES
    global TARFILES
    g=os.walk(SRC)
    for path,dir_list,file_list  in g:
             
        for file in file_list:
            fullfile=os.path.join(path,file)
            
            fileinfo=ft.guess(fullfile)
            if(fileinfo == None):
                BADFILES.append(fullfile)
                continue
            if fileinfo.extension == "tar" :
                if os.path.exists(TESTDIR):
                    shutil.rmtree(TESTDIR) 
                    os.mkdir(TESTDIR)

                untar(fullfile,TESTDIR)
                testdir(TESTDIR,fullfile)
                TARFILES+=1
            elif( fileinfo.extension == "wav"):
                testfile(fullfile,"")
            else:
                BADFILES.append(fullfile)

        # for dir in dir_list:
        #     fulldir=os.path.join(path,dir)
        #     dotest(fulldir)
       
   
if __name__ == "__main__":

    dotest(SRCPATH)
    print("*"*100)
    UNIFILE=set(FILEMD5)
    if( len(UNIFILE) != len(FILEMD5)):
        print("not all file is unique, total file: {}, unique file: {}".format(len(FILEMD5),len(UNIFILE)))
    else:
        print("unique file: {}".format(len(UNIFILE)))
    
    print("Total times: {:.2f} (hours), Unique Time:{:.2f} (hours)".format(TOTALTIME/3600,UNITIME/3600))

    print("BadFileList, len: {}, Badfile:{}".format(len(BADFILES),BADFILES))
    
    print("Tar file number: {}".format(TARFILES))
    print("*"*100)