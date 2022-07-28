
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
from physics import physicsTool
from aldenMesh import aldenConstructor
import singleRender


class compositeSpec:

    def __init__(self,information):
        self.information = information

    def compSpec(self,descIdInformation):

        descId = descIdInformation[0]

        information = self.information
        infoTransfer = informationTransfer()
        infoTransfer.startImport(descId,replaceID=0)
        env = infoTransfer.env;
        alden = infoTransfer.alden;

        env.context = 'Composite'
        env.horizonTilt = information[0]
        env.horizonSlant = information[1]
        env.sun = information[2]
        env.distance = information[3]
        env.compositeKeepAlden = descIdInformation[2]
        
        env.floor = information[4]
        env.ceiling = information[5]
        env.wallL = information[6]
        env.wallR = information[7]
        env.wallB = information[8]

        env.horizonMaterial = information[9]
        env.structureMaterial = information[10]
        env.architectureThickness = 2/100
        # alden.optical = 0
        # alden.material = information[11]            # alden with its own material, or ideal material?
        alden.scaleShiftInDepth = 0

        if descIdInformation[1] == 'onlyEnv':
            aldenConstr = aldenConstructor()
            aldenConstr.aldenSpec = alden
            aldenConstr.noAldenStimulus()
            env.architecture = 1
            env.context = 'Environment'

        elif descIdInformation[1] == 'onlyObj':
            env.floor = 0
            env.ceiling = 0
            env.wallL = 0
            env.wallR = 0
            env.wallB = 0
            alden.location = 0
            env.architecture = 0
            env.context = 'Object'

        else:
            alden.location = descIdInformation[1]
            env.architecture = 1

            if env.floor:
                alden.implantation = 0

        infoTransfer.enviroConstr.assembleEnvironment()

        if descIdInformation[1] != 'onlyEnv':
            infoTransfer.aldenConstr.aldenComplete()
            physicsToolkit = physicsTool()
            physicsToolkit.wallInteraction(alden)

        infoTransfer.exportXML(descId)
        print(descId,' ',alden.location,' DONE ')
        return


if __name__ == "__main__":

    # # redirect output to log file
    # logfile = '/Users/ecpc31/Documents/logfile_composite_spec.log'
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

    information = []

    # parse all constantAttributes
    for a in range(6,18):
        detail = sys.argv[a]

        if a in [6,7,9]:
            detail = float(detail)

        if a == 8:
            detail = [float(d) for d in detail.split(',')]

        if a in range(10,15):
            detail = int(detail)

        information.append(detail)

    # parse all possiblePositions
    possiblePositions = [int(pos) for pos in sys.argv[18:-1]]

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

    getLastGen = "SELECT count(id) FROM StimObjData WHERE instr(descId,'" +str(prefix)+"_r-"+str(runNum)+"_g-"+str(genNum)+"_l-"+str(linNum)+ "')"
    cursor.execute(getLastGen)
    lastGenNum = int(cursor.fetchone()[0]) - 1                          # get rid of the blank
    numDiffStim = int((lastGenNum-1)/(1+len(possiblePositions)*2))      # get rid of the environment-only stimulus

    descIdsUnassigned = []

    for stim in range(lastGenNum):
            descIdsUnassigned.append((str(prefix)+'_r-'+str(runNum)+'_g-'+str(genNum)+'_l-'+str(linNum)+'_s-'+str(stim)))

    db.commit()
    db.close()

    descIds = []

    # ordinary environment
    descIds.append((descIdsUnassigned[0],'onlyEnv',1))

    # ordinary objects
    for obj in range(1,numDiffStim+1):
        descIds.append((descIdsUnassigned[obj],'onlyObj',1))

    stimIndex = numDiffStim+1;

    for whichPosition in range(0,len(possiblePositions)):

        for whichStim in range(0,numDiffStim):
            descIds.append((descIdsUnassigned[stimIndex],possiblePositions[whichPosition],1))
            stimIndex += 1
            descIds.append((descIdsUnassigned[stimIndex],possiblePositions[whichPosition],0))
            stimIndex += 1

    startTime = time.time()

    p = Pool(4)
    comp = compositeSpec(information)
    p.map(comp.compSpec,descIds)

    endTime = time.time()

    print(endTime-startTime)

    # # disable output redirection
    # os.close(1)
    # os.dup(old)
    # os.close(old)

    # if int(lineage) == 1:
    #     doRender = singleRender.main()
# 0.08726646259971647 -0.6283185307179586 -0.8191520442889917,-0.5,0.5735764363510464 -0.25 0 1 1 1 1 sandOG wireframe rubber01 0 4 9 2 11 6 14 7 15 1 10 5 13 3 8 12 16 0
