
# the version with the pedestal and plants

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
            hasBack = whichCombo[5]
            hasStim = whichCombo[6]
            stimOri = whichCombo[7]
            rotationFormat = sys.argv[6]
            comCompensation = sys.argv[7]

            if rotationFormat == '50':
                pullingFrom = [1,3,5,7,9]
                stimOri = pullingFrom[stimOri]
                infoTransfer.env.context = 'GrassGravityStimulus11_' + str(whichTilt) + '-' + str(gravity) + '-' + str(secondHorizon) + '-' + str(hasBall) + '-' + str(ballBuried) + '-' + str(stimOri) + '-' + str(hasBack) + '-' + str(hasStim) + '-' + str(comCompensation)


            elif rotationFormat == '115':
                pullingFrom = [2,4,6,8,10]
                stimOri = pullingFrom[stimOri]
                infoTransfer.env.context = 'GrassGravityStimulusrevised11_' + str(whichTilt) + '-' + str(gravity) + '-' + str(secondHorizon) + '-' + str(hasBall) + '-' + str(ballBuried) + '-' + str(stimOri) + '-' + str(hasBack) + '-' + str(hasStim) + '-' + str(comCompensation)

            infoTransfer.alden.rotation = [r for r in infoTransfer.alden.stabRot]
            infoTransfer.alden.implantation = 0

        else:
            infoTransfer.env.context = 'Object'

        print(infoTransfer.env.context)

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

    getStim = "SELECT descId FROM StimObjData WHERE instr(descId,'" +str(prefix)+"_r-"+str(runNum)+"_g-"+str(genNum)+"_l-"+str(linNum)+"') ORDER BY id ASC"

    cursor.execute(getStim)
    descIdsTemp = [str(a[0]) for a in cursor.fetchall()]
    descIds = []

    for descId in descIdsTemp:
        if 'BLANK' not in descId:
            descIds.append(descId)

    db.commit()
    db.close()

    print(descIds)
    print(len(descIds))

    # 'GrassGravityStimulus2_'
    # str(whichTilt)
    # str(gravity)
    # str(secondHorizon)
    # str(hasBall)
    # str(ballBuried)
    # str(hasBack)
    # str(hasStim)
    # str(stimOri)

    rotationFormat = sys.argv[6]

    if rotationFormat == '50':
        numStimDivider = 19

    elif rotationFormat == '115':
        numStimDivider = 19

    numStim = int(round((len(descIds))/numStimDivider))

    print(numStim)
    information = []
    whichId = 0

    for stim in range(numStim):

        for whichTilt in range(3):
            information.append((descIds[whichId],[whichTilt,0,0,1,0,1,0]+[0]))
            whichId += 1

        for ori in range(5):
            # 9 possible object rotations...

            for whichTilt in range(3):
                information.append((descIds[whichId],[whichTilt,0,0,1,1,1,1,ori]))
                whichId += 1

        information.append((descIds[whichId],[]))
        whichId += 1

    print(information)

    startTime = time.time()

    p = Pool(4)
    # p = Pool(1)
    ggs = grassGravStimulus()
    p.map(ggs.generate,information)        # lineage 1

    endTime = time.time()
    print(endTime-startTime)

    # # disable output redirection
    # os.close(1)
    # os.dup(old)
    # os.close(old)
