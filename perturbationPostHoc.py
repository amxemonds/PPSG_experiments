
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


class perturbationSpec:

    def __init__(self):
        pass

    def perturbationAssigner(self,information):

        descId = information[0]
        xRot = information[1]
        yRot = information[2]
        burial = information[3]

        infoTransfer = informationTransfer()
        infoTransfer.startImport(descId,replaceID=0)
        infoTransfer.enviroConstr.assembleEnvironment()

        infoTransfer.env.context = 'Perturbation'
        # infoTransfer.alden.scaleShiftInDepth = 0
        # infoTransfer.alden.implantation = 0
        infoTransfer.alden.makePrecarious[3] = 1.0
        infoTransfer.aldenConstr.aldenComplete()
        
        # lean in various directions to various degrees
        # lean direction value (1,2,3,4), perturbation extent value (1-2)
        # translate this directly into values of rotation_euler
        # set back on ground

        bpy.ops.object.select_all(action='DESELECT')
        scn.objects.active = infoTransfer.alden.mesh
        infoTransfer.alden.mesh.select = True

        if xRot:
            bpy.ops.transform.rotate(value=xRot,axis=(1,0,0),constraint_axis=(True,False,False),constraint_orientation='GLOBAL')
            
        if yRot:
            bpy.ops.transform.rotate(value=yRot,axis=(0,1,0),constraint_axis=(False,True,False),constraint_orientation='GLOBAL')

        if burial:
            infoTransfer.alden.implantation = burial

        xMin,xMax,yMin,yMax,zMin,zMax,leeway = infoTransfer.alden.physicsToolkit.findBoundingBox(infoTransfer.alden.mesh)
        infoTransfer.alden.mesh.location[2] -= zMin

        infoTransfer.alden.rotation = [r for r in infoTransfer.alden.mesh.rotation_euler]

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
    descIds = []

    for descId in descIdsTemp:
        if 'BLANK' not in descId:
            descIds.append(descId)

    numStim = int(sys.argv[6])

    information = []
    descIdIndex = 0

    for stim in range(numStim):

        for depth in range(2):

            for xRot in range(-2,3):
                yRot = 0
                information.append((descIds[descIdIndex],xRot*perturbationLeans[0],yRot,perturbationDepths[depth]))
                descIdIndex += 1

            for yRot in range(-2,0):
                xRot = 0
                information.append((descIds[descIdIndex],xRot,yRot*perturbationLeans[0],perturbationDepths[depth]))
                descIdIndex += 1

            for yRot in range(1,3):
                xRot = 0
                information.append((descIds[descIdIndex],xRot,yRot*perturbationLeans[0],perturbationDepths[depth]))
                descIdIndex += 1

        # unchanged stimulus
        information.append((descIds[descIdIndex],0,0,0))
        descIdIndex += 1

    db.commit()
    db.close()

    startTime = time.time()

    p = Pool(4)
    perturb = perturbationSpec()
    # perturb.perturbationAssigner('180724_r-192_g-2_l-1_s-0')
    p.map(perturb.perturbationAssigner,information)

    endTime = time.time()

    print(endTime-startTime)

    # # disable output redirection
    # os.close(1)
    # os.dup(old)
    # os.close(old)

