import wave 
import os
SRC="/data/linux/audio/" #500.chinese.wav"


g=os.walk(SRC)

totaltime=0
for path,dir_list,file_list  in g:
    for file in file_list:
        fullfile=path+os.sep+file
        try:
            f=wave.open(fullfile)

        except:
            continue
        rate=f.getframerate()
        frames=f.getnframes()
        duration=frames/float(rate)
        totaltime+=duration
        print("file {}, time: {} (s)".format(fullfile,duration))

print("total: ",totaltime)

       


