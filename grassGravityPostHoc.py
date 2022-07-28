
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

from aldenMesh import aldenConstructor
from environmentPrimitives import animation, environmentSpec
from delete import deleteTool
from infoTransfer import informationTransfer


class grassGravSpec:

    def __init__(self):
        pass

    def generate(self,information):

        descId = information[0]
        whichTilt = information[1]
        gravity = information[2]
        secondHorizon = information[3]
        hasBall = information[4]
        ballBuried = information[5]
        print(information)

        env = environmentSpec()
        env.parentID = 'Grass_Gravity_Library_t-' + str(whichTilt) + '_g-' + str(gravity) + '_h-' + str(secondHorizon) + '_b-' + str(hasBall) + '_u-' + str(ballBuried)

        aldenConstr = aldenConstructor()
        alden = aldenConstr.noAldenStimulus()

        animator = animation(env)
        animator.tiltTests(whichTilt,gravity,secondHorizon)

        # need to save to XML
        exportToolkit = informationTransfer()
        exportToolkit.alden = alden
        exportToolkit.env = env
        exportToolkit.exportXML(descId)
        print(descId,' DONE')
        return


if __name__ == "__main__":

    # # redirect output to log file
    # logfile = 'logfile_random_spec.log'
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

    withoutFlat = [n for n in range(2)]
    temp = [withoutFlat.append(n) for n in range(3,len(horizonTiltOptions))]
    combosNoBall = [[n,1,1,0,0] for n in range(len(horizonTiltOptions))] + [[n,1,0,0,0] for n in withoutFlat] + [[n,0,0,0,0] for n in withoutFlat]
    combosBuriedBall = [[n,1,1,1,1] for n in range(len(horizonTiltOptions))] + [[n,1,0,1,1] for n in withoutFlat] + [[n,0,0,1,1] for n in withoutFlat]
    combosUnburiedBall = [[n,1,1,1,0] for n in range(len(horizonTiltOptions))] + [[n,1,0,1,0] for n in withoutFlat] + [[n,0,0,1,0] for n in withoutFlat]
    combos = combosNoBall + combosBuriedBall + combosUnburiedBall

    information = []

    for ind in range(len(combos)):
        information.append([descIds[ind]]+combos[ind])

    print(descIds)

    db.commit()
    db.close()

    startTime = time.time()

    p = Pool(4)
    ggs = grassGravSpec()
    p.map(ggs.generate,information)

    endTime = time.time()

    print(endTime-startTime)

    # # disable output redirection
    # os.close(1)
    # os.dup(old)
    # os.close(old)

