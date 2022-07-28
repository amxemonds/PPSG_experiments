

# CURRENTLY SUPPORTS ONLY ONE POST-HOC STIMULUS PER LINEAGE

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

from mathutils import Vector
from mathutils import Euler

import config
from config import *

from infoTransfer import informationTransfer
from delete import deleteTool
from aldenMesh import aldenSkeleton

from morphSpec import applyMorph
import singleRender


class stabilitySpec:

    def __init__(self):
        
        self.descId = None

    def stabSpec(self,information):

        descId = information[0]
        alterationOfPotential = information[1]
        burial = information[2]

        infoTransfer = informationTransfer()
        infoTransfer.startImport(descId)
        infoTransfer.enviroConstr.assembleEnvironment()

        alden = infoTransfer.alden
        alden.densityUniform = 1
        alden.affectedLimbs = []
        alden.limbMaterials = []

        infoTransfer.env.context = 'Stability'

        isPrecarious = False

        if sum([alden.makePrecarious[n] for n in range(3)]) and alden.makePrecarious[3]:
            isPrecarious = True

        if alterationOfPotential: 
            # if in second set of numMorph stimuli, do complement of default potential and precariousness

            if bool(alden.lowPotentialEnergy) and isPrecarious: # is low potential and is precarious:
                # if originally low potential and originally precarious, also low potential and no precarious
                # alden.lowPotentialEnergy = 1
                alden.makePrecarious[3] = 0.0

            elif not bool(alden.lowPotentialEnergy) and isPrecarious: # is high potential and is precarious:
                # if originally high potential and originally precarious, also low potential and no precarious
                # alden.lowPotentialEnergy = 1
                alden.makePrecarious[3] = 0.0

            elif not bool(alden.lowPotentialEnergy) and not isPrecarious: # is high potential and is not precarious:
                # if originally high potential and originally no precarious, also low potential and no precarious
                # alden.lowPotentialEnergy = 1
                alden.makePrecarious[3] = 0.0

            elif bool(alden.lowPotentialEnergy) and not isPrecarious: # is low potential and is not precarious:
                # if originally low potential and originally no precarious, also high potential and no precarious
                alden.lowPotentialEnergy = 0
                alden.makePrecarious[3] = 1.0
                
                alden.mesh.rotation_euler = Euler(([0.0,0.0,0.0]))
                alden.rotation = [0.0,0.0,0.0]

            # alden.makePrecarious[3] = 0.0
            # print(alden.makePrecarious)

        alden.implantation = burial
        # alden.scaleShiftInDepth = 0

        infoTransfer.aldenConstr.aldenComplete()
        infoTransfer.exportXML(descId)
        print(information,' DONE ')
        return


if __name__ == "__main__":

    # # redirect output to log file
    # logfile = '/Users/ecpc31/Documents/logfile_stability_spec.log'
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

    infoTransfer = informationTransfer()

    numStim = int(sys.argv[6])
    numMorphs = int(sys.argv[7])
    stimInd = 0
    descIds = []
    stim = 0

    for s in range(numStim):

        for morph in range(numMorphs*2):

            if morph >= numMorphs:
                alterationOfPotential = 1

            else:
                alterationOfPotential = 0

            burial = burialDepth[stimInd]
            descIds.append([str(prefix)+'_r-'+str(runNum)+'_g-'+str(genNum)+'_l-'+str(linNum)+'_s-'+str(stim),alterationOfPotential,burial])
            stim += 1
            
            if stimInd == numMorphs-1:
                stimInd = 0

            else:
                stimInd += 1

    db.commit()
    db.close()

    startTime = time.time()

    p = Pool(4)
    stab = stabilitySpec()
    p.map(stab.stabSpec,descIds)

    endTime = time.time()

    print(endTime-startTime)

    # # disable output redirection
    # os.close(1)
    # os.dup(old)
    # os.close(old)

    # doRender = singleRender.main()
