

# CURRENTLY SUPPORTS ONLY ONE POST-HOC STIMULUS PER LINEAGE

import bpy
import sys
import os
from multiprocessing import Pool
import time
import random
from itertools import combinations
import math

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

from morphSpec import applyMorph
import singleRender


class densitySpec:

    def __init__(self):
        self.alternateMaterial = None
        pass

    def denSpec(self,information):

        descId = information[0]
        whichLimbs = information[1]

        infoTransfer = informationTransfer()
        infoTransfer.startImport(descId)
        infoTransfer.enviroConstr.assembleEnvironment()

        infoTransfer.env.context = 'Density'
        # infoTransfer.alden.scaleShiftInDepth = 0
        # infoTransfer.alden.implantation = 0
        infoTransfer.alden.howMany = len(whichLimbs)

        if len(whichLimbs) != 0:
            infoTransfer.alden.densityUniform = 0

            for ind in range(len(whichLimbs)):
                infoTransfer.alden.affectedLimbs.append(whichLimbs[ind])
                infoTransfer.alden.limbMaterials.append(self.alternateMaterial)

        else:
            infoTransfer.alden.densityUniform = 1

        infoTransfer.aldenConstr.aldenComplete()
        infoTransfer.exportXML(descId)
        print(descId,' ',whichLimbs,' DONE ')
        return


if __name__ == "__main__":

    # redirect output to log file
    logfile = '/Users/ecpc31/Documents/logfile_density_spec.log'
    open(logfile, 'a').close()
    old = os.dup(1)
    sys.stdout.flush()
    os.close(1)
    os.open(logfile, os.O_WRONLY)

    # use blender render engine
    scn.render.engine = 'BLENDER_RENDER'
    scn.frame_end = totalFrames

    # clear cache, delete objects
    bpy.ops.ptcache.free_bake_all()
    deleteToolkit = deleteTool()
    deleteToolkit.deleteAllMaterials()
    deleteToolkit.deleteAllObjects()

    # collect all stims from last generation, split by lineage
    # look for all different stimulusIDs in blenderspecs and split up (NOT IMPLEMENTED)

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
    lastGenNum = int(cursor.fetchone()[0]) - 1
    nComponents = int(sys.argv[6])
    whichLimbs = []

    for ind in range(nComponents+1):
        combos = list(combinations(range(nComponents),ind))
        w = [whichLimbs.append(c) for c in combos]

    descIds = []

    for stim in range(lastGenNum):
        descIds.append(((str(prefix)+'_r-'+str(runNum)+'_g-'+str(genNum)+'_l-'+str(linNum)+'_s-'+str(stim)),whichLimbs[stim]))

    db.commit()
    db.close()

    startTime = time.time()

    p = Pool(4)
    den = densitySpec()
    den.alternateMaterial = sys.argv[7]
    p.map(den.denSpec,descIds)        # lineage 1

    endTime = time.time()

    print(endTime-startTime)

    # disable output redirection
    os.close(1)
    os.dup(old)
    os.close(old)

    # doRender = singleRender.main()


