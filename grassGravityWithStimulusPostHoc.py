
import bpy
import sys
import os
from multiprocessing import Pool
import time

sys.path.append("/usr/local/lib/python3.6/site-packages")
sys.path.append("/Library/Frameworks/Python.framework/Versions/3.6/lib/python3.6/site-packages")
sys.path.append("/Library/Python/2.7/site-packages")

import mysql.connector

dir = os.path.dirname(bpy.data.filepath)
if not dir in sys.path:
    sys.path.append(dir)
    sys.path.append(dir+'/Morphs/')
    sys.path.append(dir+'/Primitives/')

import config
from config import *

from infoTransfer import informationTransfer
from delete import deleteTool


class grassGravStimulus:

    def __init__(self):
        pass
        
    def generate(self,information):

        descId = information[0]
        whichCombo = information[1]

        infoTransfer = informationTransfer()
        infoTransfer.startImport(descId,replaceID=0)
        infoTransfer.enviroConstr.assembleEnvironment()

        if whichCombo:
            whichTilt = whichCombo[0]
            gravity = whichCombo[1]
            secondHorizon = whichCombo[2]
            hasBall = whichCombo[3]
            ballBuried = whichCombo[4]
            stimOri = whichCombo[5]
            infoTransfer.env.context = 'GrassGravityStimulus_' + str(whichTilt) + '-' + str(gravity) + '-' + str(secondHorizon) + '-' + str(hasBall) + '-' + str(ballBuried) + '-' + str(stimOri)
            infoTransfer.alden.rotation = [r for r in infoTransfer.alden.stabRot]

        else:
            infoTransfer.env.context = 'Object'

        infoTransfer.aldenConstr.aldenComplete()

        infoTransfer.exportXML(descId)
        print(descId,' DONE ')
        return


if __name__ == "__main__":

    # # redirect output to log file
    # logfile = 'logfile_gs_spec.log'
    # open(logfile, 'a').close()
    # old = os.dup(1)
    # sys.stdout.flush()
    # os.close(1)
    # os.open(logfile, os.O_WRONLY)

    # use blender render engine
    scn.render.engine = 'BLENDER_RENDER'
    scn.frame_end = totalFrames

    # clear cache, delete objects
    bpy.ops.ptcache.free_bake_all()
    deleteToolkit = deleteTool()
    deleteToolkit.deleteAllMaterials()
    deleteToolkit.deleteAllObjects()

    db = mysql.connector.connect(user='xper_rw', password='up2nite', host=databaseIP, database=databaseName,charset='utf8',use_unicode=True)
    cursor = db.cursor()
    
    getPre = "SELECT prefix FROM DescriptiveInfo WHERE tstamp = (SELECT max(tstamp) FROM DescriptiveInfo)"
    getRun = "SELECT gaRun FROM DescriptiveInfo WHERE tstamp = (SELECT max(tstamp) FROM DescriptiveInfo)"
    getGen = "SELECT genNum FROM DescriptiveInfo WHERE tstamp = (SELECT max(tstamp) FROM DescriptiveInfo)"
    getLin = "SELECT linNum FROM DescriptiveInfo WHERE tstamp = (SELECT max(tstamp) FROM DescriptiveInfo)"

    cursor.execute(getPre)
    prefix = cursor.fetchone()[0]

    cursor.execute(getRun)
    runNum = cursor.fetchone()[0]

    cursor.execute(getGen)
    genNum = cursor.fetchone()[0]

    cursor.execute(getLin)
    linNum = cursor.fetchone()[0]

    getStim = "SELECT descId FROM StimObjData WHERE instr(descId,'" +str(prefix)+"_r-"+str(runNum)+"_g-"+str(genNum)+"_l-"+str(linNum)+"')"

    cursor.execute(getStim)
    descIdsTemp = [str(a[0]) for a in cursor.fetchall()]
    descIds = []

    for descId in descIdsTemp:
        if 'BLANK' not in descId:
            descIds.append(descId)

    # num. t. g. h.
    # 0    0  1  1
    # 1    1  1  1
    # 2    2  1  1
    # 3    3  1  1
    # 4    4  1  1
    # 5    5  1  1
    # 6    6  1  1
    # 7    7  1  1
    # 8    8  1  1
    # -
    # 9    1  1  0
    # 10   2  1  0
    # 11   3  1  0
    # 12   0  1  0
    # 13   5  1  0
    # 14   6  1  0
    # 15   7  1  0
    # 16   8  1  0
    # -
    # 17   1  0  0
    # 18   2  0  0
    # 19   3  0  0
    # 20   0  0  0
    # 21   5  0  0
    # 22   6  0  0
    # 23   7  0  0
    # 24   8  0  0

    db.commit()
    db.close()

    withoutFlat = [n for n in range(2)]
    temp = [withoutFlat.append(n) for n in range(3,len(horizonTiltOptions))]
    combosBuriedStimulus = [[n,1,1,1,1] for n in range(len(horizonTiltOptions))] + [[n,1,0,1,1] for n in withoutFlat] + [[n,0,0,1,1] for n in withoutFlat]
    combosUnburiedStimulus = [[n,1,1,1,0] for n in range(len(horizonTiltOptions))] + [[n,1,0,1,0] for n in withoutFlat] + [[n,0,0,1,0] for n in withoutFlat]
    combos = combosBuriedStimulus + combosUnburiedStimulus

    numStim = int(round(len(descIds)/53))
    information = []
    whichId = 0

    for stim in range(numStim):

        for ori in range(2):

            for position in range(26):

                information.append((descIds[whichId],combos[position]+[ori]))
                whichId += 1

        information.append((descIds[whichId],[]))

    print(information)

    startTime = time.time()

    p = Pool(4)
    ggs = grassGravStimulus()
    p.map(ggs.generate,information)        # lineage 1

    endTime = time.time()
    print(endTime-startTime)

    # # disable output redirection
    # os.close(1)
    # os.dup(old)
    # os.close(old)
