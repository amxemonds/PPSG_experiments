
import bpy
import sys
import os
import random
import math

dir = os.path.dirname(bpy.data.filepath)
if not dir in sys.path:
    sys.path.append(dir)
    sys.path.append(dir+'/Morphs/')
    sys.path.append(dir+'/Primitives/')

import config
from config import *

from aldenMesh import aldenConstructor, aldenObjectSpec
from environmentPrimitives import animation, environmentSpec, enclosureConstructor, environmentConstructor
from delete import deleteTool
from stimulusRender import stimulusRender

from infoTransfer import informationTransfer


class grassGravLibrary:

    def __init__(self,combos):

        self.combos = combos
        self.deleteToolkit = deleteTool()
        self.__generate()
        
    def __generate(self):

        env = environmentSpec()
        aldenConstr = aldenConstructor()
        alden = aldenConstr.noAldenStimulus()
        animator = animation(env)

        for whichCombo in self.combos:
            self.deleteToolkit.deleteAllMaterials()
            self.deleteToolkit.deleteAllObjects()
            
            whichTilt = whichCombo[0]
            gravity = whichCombo[1]
            secondHorizon = whichCombo[2]
            hasBall = whichCombo[3]
            ballBuried = whichCombo[4]
            animator.tiltTests(whichTilt,gravity,secondHorizon,hasBall,ballBuried)

            alden.id = 'Grass_Gravity_Library_t-' + str(whichTilt) + '_g-' + str(gravity) + '_h-' + str(secondHorizon) + '_b-' + str(hasBall) + '_u-' + str(ballBuried)        
            env.stimulusID = 'Grass_Gravity_Library_t-' + str(whichTilt) + '_g-' + str(gravity) + '_h-' + str(secondHorizon) + '_b-' + str(hasBall) + '_u-' + str(ballBuried)
        
            if usesOccluder:
                enviroConstr = environmentConstructor(env)
                enviroConstr.gaussianOccluder()

            # need to save to XML, perhaps render
            # renderToolkit = informationTransfer()
            # renderToolkit.alden = alden
            # renderToolkit.env = env
            # renderToolkit.exportXML()

            self.render(alden,env)
            print(alden.id,' DONE')

            animator.restoreEnvironmentVisibility()
        return

    def render(self,alden,env):

        render = stimulusRender(alden,env)
        render.renderStill()
        return


if __name__ == "__main__":

    # # redirect output to log file
    # logfile = '/Users/ecpc31/Documents/logfile_grassGrav_spec.log'
    # open(logfile, 'a').close()
    # old = os.dup(1)
    # sys.stdout.flush()
    # os.close(1)
    # os.open(logfile, os.O_WRONLY)

    # use cycles render engine
    scn.render.engine = 'CYCLES'
    bpy.context.user_preferences.addons['cycles'].preferences.compute_device_type = 'CUDA'
    bpy.context.user_preferences.addons['cycles'].preferences.devices[0].use = True
    # bpy.context.user_preferences.addons['cycles'].preferences.devices[1].use = True
    # bpy.context.user_preferences.addons['cycles'].preferences.devices[2].use = True
    scn.frame_end = totalFrames

    # clear cache, delete objects
    bpy.ops.ptcache.free_bake_all()
    deleteToolkit = deleteTool()
    deleteToolkit.deleteAllMaterials()
    deleteToolkit.deleteAllObjects()

    # num. t. g. h.
    # 0    0  1  1
    # 1    1  1  1
    # 2    2  1  1
    # 3    3  1  1
    # 4    4  1  1
    # 5    5  1  1
    # 6    6  1  1
    # 7    7  1  1
    # 8    8  1  1
    # -
    # 9    1  1  0
    # 10   2  1  0
    # 11   3  1  0
    # 12   0  1  0
    # 13   5  1  0
    # 14   6  1  0
    # 15   7  1  0
    # 16   8  1  0
    # -
    # 17   1  0  0
    # 18   2  0  0
    # 19   3  0  0
    # 20   0  0  0
    # 21   5  0  0
    # 22   6  0  0
    # 23   7  0  0
    # 24   8  0  0

    withoutFlat = [n for n in range(2)]
    temp = [withoutFlat.append(n) for n in range(3,len(horizonTiltOptions))]
    combosNoBall = [[n,1,1,0,0] for n in range(len(horizonTiltOptions))] + [[n,1,0,0,0] for n in withoutFlat] + [[n,0,0,0,0] for n in withoutFlat]
    combosBuriedBall = [[n,1,1,1,1] for n in range(len(horizonTiltOptions))] + [[n,1,0,1,1] for n in withoutFlat] + [[n,0,0,1,1] for n in withoutFlat]
    combosUnburiedBall = [[n,1,1,1,0] for n in range(len(horizonTiltOptions))] + [[n,1,0,1,0] for n in withoutFlat] + [[n,0,0,1,0] for n in withoutFlat]
    combos = combosNoBall + combosBuriedBall + combosUnburiedBall

    generate = grassGravLibrary(combos)
    # generate = grassGravLibrary([[0,1,1]])

    # # disable output redirection
    # os.close(1)
    # os.dup(old)
    # os.close(old)
