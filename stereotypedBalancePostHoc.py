
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
from environmentPrimitives import animation, environmentSpec, environmentConstructor
from delete import deleteTool
from infoTransfer import informationTransfer


class stereotypedBalanceSpec:

    def __init__(self):
        pass

    def generate(self,information):

        descId = information[0]
        whichOri = information[1]
        whichRot = information[2]
        print(information)

        env = environmentSpec()
        env.parentID = 'Stereotyped_Balance_Library_o-' + str(whichOri) + '_r-' +str(whichRot)

        aldenConstr = aldenConstructor()
        alden = aldenConstr.noAldenStimulus()

        enviroConstr = environmentConstructor(env)
        env.horizon = enviroConstr.tiltHorizon()
        enviroConstr.tiltPeripherals()

        animator = animation(env)
        animator.tiltSkySetup()

        env.horizonSlant = 0
        env.horizonTilt = 0
        env.gravity = 1
        env.compositeKeepAlden = 0
        env.horizonMaterial = 'ground08'
        env.context = 'StereotypedBalance'
        env.fixationPointDepth = 3.0

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
    # scn.render.engine = 'CYCLES'
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

    combos = [[o,r] for o in range(1,12) for r in range(0,4)]
    information = []

    for ind in range(len(combos)):
        information.append([descIds[ind]]+combos[ind])

    print(descIds)

    db.commit()
    db.close()

    startTime = time.time()

    p = Pool(4)
    sbs = stereotypedBalanceSpec()
    p.map(sbs.generate,information)

    endTime = time.time()

    print(endTime-startTime)

    # # disable output redirection
    # os.close(1)
    # os.dup(old)
    # os.close(old)

