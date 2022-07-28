
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


class cannedSpec:

    def __init__(self):
        pass

    def cannedDetermination(self,information):

        descId = information[0]
        whichMaterial = information[1]

        infoTransfer = informationTransfer()
        infoTransfer.startImport(descId,replaceID=0)
        infoTransfer.enviroConstr.assembleEnvironment()
        print(descId)

        if whichMaterial != None:
            print('MATERIAL')
            infoTransfer.env.context = 'Material'
            infoTransfer.alden.material = culledAldenMaterialOptions[whichMaterial]
            infoTransfer.alden.optical = 0
            
        else:
            infoTransfer.env.context = 'Object'

        infoTransfer.aldenConstr.aldenComplete()
        infoTransfer.exportXML(descId)
        print(descId,' DONE ')        
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

    numStim = int(round(len(descIds)/31))
    information = []
    whichId = 0

    for stim in range(numStim):
        for n in range(30):
            information.append((descIds[whichId],n))
            whichId += 1

        information.append((descIds[whichId],None))
        whichId += 1

    startTime = time.time()

    # print(information)

    p = Pool(4)
    canspec = cannedSpec()
    p.map(canspec.cannedDetermination,information)

    endTime = time.time()

    print(endTime-startTime)

    # # disable output redirection
    # os.close(1)
    # os.dup(old)
    # os.close(old)

