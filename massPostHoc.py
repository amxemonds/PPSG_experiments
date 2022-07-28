
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
from environmentPrimitives import animation


class massSpec:

    def __init__(self):
        pass

    def massLimbFinder(self,descId):

        infoTransfer = informationTransfer()
        infoTransfer.startImport(descId)
        infoTransfer.enviroConstr.assembleEnvironment()
        infoTransfer.env.context = 'Mass'
        print(descId)
        # infoTransfer.alden.scaleShiftInDepth = 0
        # infoTransfer.alden.implantation = 0
        infoTransfer.alden.makePrecarious[3] = 0.0
        infoTransfer.aldenConstr.aldenComplete()
        
        animator = animation(infoTransfer.env)
        animator.aldenSpec = infoTransfer.alden

        infoTransfer.enviroConstr.findBoneLocations(infoTransfer.alden)
        whichLimbs = [ind for ind,entry in enumerate(infoTransfer.alden.boneTags)]
        # com = infoTransfer.alden.physicsToolkit.centerOfMassByVolume(infoTransfer.alden)

        maxLimbDistances = []

        for limb in whichLimbs:
            head = infoTransfer.alden.headsTails[limb][0]
            tail = infoTransfer.alden.headsTails[limb][1]

            # # farthest from com in x,y
            # distHeadCom = math.sqrt((com[0]-head[0])**2+(com[1]-head[1])**2)
            # distTailCom = math.sqrt((com[0]-tail[0])**2+(com[1]-tail[1])**2)
            # maxLimbDistances.append(max(distHeadCom,distTailCom))

            distanceZhead = head[2]
            distanceZtail = tail[2]
            maxLimbDistances.append(max(distanceZhead,distanceZtail))

        maxLimbInd = infoTransfer.alden.compOrder[maxLimbDistances.index(max(maxLimbDistances))]
        infoTransfer.alden.massManipulationLimb = maxLimbInd

        infoTransfer.exportXML(descId)
        print(descId,' DONE ',infoTransfer.alden.compOrder,infoTransfer.alden.massManipulationLimb)
        return


if __name__ == "__main__":

    # # redirect output to log file
    # logfile = '/Users/ecpc31/Documents/logfile_animate_spec.log'
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
    print(getStim)

    cursor.execute(getStim)
    descIdsTemp = [str(a[0]) for a in cursor.fetchall()]
    print(descIdsTemp)
    descIds = []

    for descId in descIdsTemp:
        if 'BLANK' not in descId:
            descIds.append(descId)

    db.commit()
    db.close()

    startTime = time.time()

    p = Pool(4)
    mass = massSpec()
    # mass.massLimbFinder('180724_r-192_g-2_l-1_s-0')
    p.map(mass.massLimbFinder,descIds)

    endTime = time.time()

    print(endTime-startTime)

    # # disable output redirection
    # os.close(1)
    # os.dup(old)
    # os.close(old)

