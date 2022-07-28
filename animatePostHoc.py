

# CURRENTLY SUPPORTS ONLY THREE POST-HOC STIMULI PER LINEAGE

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
import singleRender


class animateSpec:

    def __init__(self,targetedColoration):
        self.targetedColoration = targetedColoration

    def aniSpec(self,information):

        descId = information[0]
        wiggleIndex = information[1]
        whichType = information[2]
        whichMaterial = information[3]

        infoTransfer = informationTransfer()
        infoTransfer.startImport(descId,instantImport=1,replaceID=0)
        infoTransfer.enviroConstr.invisibleAssembleEnvironment()
        # at start import, have env.stimulus and alden.id, which refer to the parent stimulus.
        # don't save any meshes and refer only to the parent stimulus in this post hoc? sure, why not.
        # wait, this is already good to go...

        # infoTransfer.alden.scaleShiftInDepth = 0
        # infoTransfer.alden.implantation = 0
        infoTransfer.alden.densityUniform = 1
        infoTransfer.env.context = whichType
        infoTransfer.alden.rotation = [r for r in infoTransfer.alden.stabRot]
        # infoTransfer.aldenConstr.aldenComplete()

        if wiggleIndex >= 0: # not a plain stimulus
            animator = animation(infoTransfer.env)
            animator.aldenSpec = infoTransfer.alden
            whichLimbs,limbComps = animator.wigglePossibilities()
            infoTransfer.alden.whichWiggle = limbComps[whichLimbs[wiggleIndex]]

            if targetedColoration:
                # limit new material coloration to the limb of interest
                infoTransfer.alden.densityUniform = 0
                infoTransfer.alden.affectedLimbs = [limbComps.index(infoTransfer.alden.whichWiggle)]
                infoTransfer.alden.limbMaterials = [whichMaterial]

            else:
                # new material coloration applies to whole object
                infoTransfer.alden.densityUniform = 1
                infoTransfer.alden.affectedLimbs = []
                infoTransfer.alden.limbMaterials = []
                infoTransfer.alden.material = whichMaterial
                infoTransfer.alden.optical = 0

        if wiggleIndex == -1: # plain stimulus with uniform material
            infoTransfer.alden.densityUniform = 1
            infoTransfer.alden.affectedLimbs = []
            infoTransfer.alden.limbMaterials = []
            infoTransfer.alden.material = whichMaterial
            infoTransfer.alden.optical = 0

        infoTransfer.exportXML(descId)
        print(information,' DONE ')
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

    numMaterials = int(sys.argv[6])
    numStimPerLineage = int(sys.argv[7])
    targetedColoration = int(sys.argv[8])
    numLegsIndex = 9 # sys.argv[9]

    descIds = []
    stim = 0
    
    for objectNumber in range(numStimPerLineage):

        descIds.append(((str(prefix)+'_r-'+str(runNum)+'_g-'+str(genNum)+'_l-'+str(linNum)+'_s-'+str(stim)),-2,'Object',None))
        stim += 1

        if objectNumber%2==0:

            descIds.append(((str(prefix)+'_r-'+str(runNum)+'_g-'+str(genNum)+'_l-'+str(linNum)+'_s-'+str(stim)),-1,'Object','fur01'))
            stim += 1

            for leg in range(int(sys.argv[numLegsIndex])):

                descIds.append(((str(prefix)+'_r-'+str(runNum)+'_g-'+str(genNum)+'_l-'+str(linNum)+'_s-'+str(stim)),leg,'Animate','fur01'))
                stim += 1

        else:

            descIds.append(((str(prefix)+'_r-'+str(runNum)+'_g-'+str(genNum)+'_l-'+str(linNum)+'_s-'+str(stim)),-1,'Object','fur01'))
            stim += 1

        numLegsIndex += 1

    print(descIds)

    db.commit()
    db.close()

    startTime = time.time()

    p = Pool(4)
    ani = animateSpec(targetedColoration)
    p.map(ani.aniSpec,descIds)        # lineage 1

    endTime = time.time()

    print(endTime-startTime)
# /Applications/blender-279/Blender.app/Contents/MacOS/blender /Users/ecpc31/Dropbox/Blender/ProgressionClasses/frameRate.blend --background --python /Users/ecpc31/Dropbox/Blender/ProgressionClasses/animatePostHoc.py -- 4 3 3 3 1 2 1 1

    # # disable output redirection
    # os.close(1)
    # os.dup(old)
    # os.close(old)

    # doRender = singleRender.main()

#-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-#

    # one lineage is:

# UNALTERED STIMULUS
    # 0. plain static object 1
    # 1. plain static object 1
    # 2. plain static object 1

# LIMB ONE
    # 3. limb 1 static object 1 squish 1
    # 4. limb 1 animate object 1 squish 1
    # 5. limb 1 static object 1 squish 1

    # 6. limb 1 static object 1 squish 2
    # 7. limb 1 animate object 1 squish 2
    # 8. limb 1 static object 1 squish 2

    # 9. limb 1 static object 1 squish 3
    # 10. limb 1 animate object 1 squish 3
    # 11. limb 1 static object 1 squish 3

    # 12. limb 1 static object 1 squish 4
    # 13. limb 1 animate object 1 squish 4
    # 14. limb 1 static object 1 squish 4

    # 15. limb 1 static object 1 stiff 1
    # 16. limb 1 static object 1 stiff 1
    # 17. limb 1 static object 1 stiff 1

    # 18. limb 1 static object 1 stiff 2
    # 19. limb 1 static object 1 stiff 2
    # 20. limb 1 static object 1 stiff 2

    # 21. limb 1 static object 1 stiff 3
    # 22. limb 1 static object 1 stiff 3
    # 23. limb 1 static object 1 stiff 3

    # 24. limb 1 static object 1 stiff 4
    # 25. limb 1 static object 1 stiff 4
    # 26. limb 1 static object 1 stiff 4

# LIMB TWO
    # 27. limb 2 static object 1 squish 1
    # 28. limb 2 animate object 1 squish 1
    # 29. limb 2 static object 1 squish 1

    # 30. limb 2 static object 1 squish 2
    # 31. limb 2 animate object 1 squish 2
    # 32. limb 2 static object 1 squish 2

    # 33. limb 2 static object 1 squish 3
    # 34. limb 2 animate object 1 squish 3
    # 35. limb 2 static object 1 squish 3

    # 36. limb 2 static object 1 squish 4
    # 37. limb 2 animate object 1 squish 4
    # 38. limb 2 static object 1 squish 4

    # 39. limb 2 static object 1 stiff 1
    # 40. limb 2 static object 1 stiff 1
    # 41. limb 2 static object 1 stiff 1

    # 42. limb 2 static object 1 stiff 2
    # 43. limb 2 static object 1 stiff 2
    # 44. limb 2 static object 1 stiff 2

    # 45. limb 2 static object 1 stiff 3
    # 46. limb 2 static object 1 stiff 3
    # 47. limb 2 static object 1 stiff 3

    # 48. limb 2 static object 1 stiff 4
    # 49. limb 2 static object 1 stiff 4
    # 50. limb 2 static object 1 stiff 4

# LIMB THREE
    # 51. limb 3 static object 1 squish 1
    # 52. limb 3 animate object 1 squish 1
    # 53. limb 3 static object 1 squish 1

    # 54. limb 3 static object 1 squish 2
    # 55. limb 3 animate object 1 squish 2
    # 56. limb 3 static object 1 squish 2

    # 57. limb 3 static object 1 squish 3
    # 58. limb 3 animate object 1 squish 3
    # 59. limb 3 static object 1 squish 3

    # 60. limb 3 static object 1 squish 4
    # 61. limb 3 animate object 1 squish 4
    # 62. limb 3 static object 1 squish 4

    # 63. limb 3 static object 1 stiff 1
    # 64. limb 3 static object 1 stiff 1
    # 65. limb 3 static object 1 stiff 1

    # 66. limb 3 static object 1 stiff 2
    # 67. limb 3 static object 1 stiff 2
    # 68. limb 3 static object 1 stiff 2

    # 69. limb 3 static object 1 stiff 3
    # 70. limb 3 static object 1 stiff 3
    # 71. limb 3 static object 1 stiff 3

    # 72. limb 3 static object 1 stiff 4
    # 73. limb 3 static object 1 stiff 4
    # 74. limb 3 static object 1 stiff 4

# LINEAGE 1
# OBJECT ONE: 75 STIMULI
# OBJECT TWO: 75 STIMULI
# OBJECT THREE: 75 STIMULI

# LINEAGE 2
# OBJECT ONE: 75 STIMULI
# OBJECT TWO: 75 STIMULI
# OBJECT THREE: 75 STIMULI

# TOTAL STIMULI: 450
