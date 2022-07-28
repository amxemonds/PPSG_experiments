
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


class distanceSpec:
    # right now, just stick morph or just blender morph.

    def __init__(self):
        pass

    def distanceChange(self,information):

        descId = information[0]
        distance = information[1]
        retinalSize = information[2]

        infoTransfer = informationTransfer()
        infoTransfer.startImport(descId,replaceID=0)
        infoTransfer.alden.rotation = [r for r in infoTransfer.alden.stabRot]
        print(descId)

        if distance != None:
            print(descId,'here')
            infoTransfer.alden.scaleShiftInDepth = distance

        infoTransfer.alden.consistentRetinalSize = retinalSize
        infoTransfer.env.context = 'Object'
        infoTransfer.exportXML(descId)
        print(descId,' DONE ')
        return


if __name__ == "__main__":

    # # redirect output to log file
    # logfile = 'logfile_restore_spec.log'
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
    print(getStim)

    cursor.execute(getStim)
    descIdsTemp = [str(a[0]) for a in cursor.fetchall()]
    print(descIdsTemp)

    descIds = []

    for descId in descIdsTemp:
        if 'BLANK' not in descId:
            descIds.append(descId)

    information = []

    objCounts = int(sys.argv[6])
    distanceCounts = int(sys.argv[7])
    stim = 0

    distanceCounts = int((distanceCounts-1)/2+1)

    for obj in range(objCounts):

        for distance in range(distanceCounts):

            if distance == 0:
                # make it the original stimulus
                information.append([descIds[stim],None,1])
                stim += 1

            else:
                information.append([descIds[stim],distance/distanceCounts*3,1])
                information.append([descIds[stim+1],distance/distanceCounts*3,0])
                stim += 2

    db.commit()
    db.close()

    # count to see how many individual stimuli...
    # one blocky and one not for each stim identity...

    startTime = time.time()

    p = Pool(8) # what is the correct number here?
    ds = distanceSpec()
    p.map(ds.distanceChange,information)

    endTime = time.time()

    print(endTime-startTime)

    # # disable output redirection
    # os.close(1)
    # os.dup(old)
    # os.close(old)

