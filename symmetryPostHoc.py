
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


class symmetrySpec:
    # right now, just stick morph or just blender morph.

    def __init__(self):
        pass

    def alterSymmetry(self,information):

        descId = information[0]
        symmetryMod = information[1]

        # [bilateral symmetry, rotate 180, mirror]
        bilateral = symmetryMod[0]
        rot180 = symmetryMod[1]
        mirror = symmetryMod[2]

        infoTransfer = informationTransfer()
        infoTransfer.startImport(descId,replaceID=0)
        infoTransfer.alden.rotation = [r for r in infoTransfer.alden.stabRot]
        infoTransfer.env.context = 'Symmetry_' + str(bilateral) + '-' + str(rot180) + '-' + str(mirror)
        infoTransfer.alden.blocky = int(bilateral)
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
    descIds = [str(a[0]) for a in cursor.fetchall()]
    print(descIds)

    db.commit()
    db.close()

    numStim = (len(descIds)-1)/4
    information = []
    whichId = 0

    # [bilateral symmetry, rotate 180, mirror]
    symmetryModifications = [[0,0,0],[1,0,0],[0,1,0],[0,0,1]]

    for stim in range(numStim):

        for symmetryMod in symmetryModifications:

                information.append((descIds[whichId],symmetryMod))
                whichId += 1

    print(information)

    startTime = time.time()

    p = Pool(8) # what is the correct number here?
    bl = blockySpec()
    p.map(bl.methodicalBlockification,information)

    endTime = time.time()

    print(endTime-startTime)

    # # disable output redirection
    # os.close(1)
    # os.dup(old)
    # os.close(old)

