
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

from aldenMesh import aldenConstructor
from environmentPrimitives import animation, environmentSpec, enclosureConstructor, environmentConstructor
from infoTransfer import informationTransfer
from delete import deleteTool
from stimulusRender import stimulusRender


class autoAnimate:

    def __init__(self):

        self.deleteToolkit = deleteTool()
        self.renderToolkit = informationTransfer()
        self.generate()
        
    def generate(self):

        env = environmentSpec()
        enclosConstr = enclosureConstructor(env)
        enclosConstr.noEnclosure(alden=0)

        aldenConstr = aldenConstructor()
        alden = aldenConstr.noAldenStimulus()
        animator = animation(env)

        for angle in range(-4,1):
            self.deleteToolkit.deleteAllMaterials()
            self.deleteToolkit.deleteAllObjects()

            alden.id = 'Roll_Animation_Library_' + str(angle)            
            env.stimulusID = str(angle)

            angle = angle/4*math.pi
            animator.rollTests(angle)

            if usesOccluder:
                enviroConstr = environmentConstructor(env)
                enviroConstr.gaussianOccluder()

            # need to save to XML, perhaps render
            # renderToolkit = informationTransfer()
            # renderToolkit.alden = alden
            # renderToolkit.env = env
            # renderToolkit.exportXML()
            # # renderToolkit.renderStill()

            self.render(alden,env)
            print(alden.id,' DONE')

        return

    def render(self,alden,env):

        render = stimulusRender(alden,env)
        render.renderAnimation(duplicate=False,frames=40)
        return


if __name__ == "__main__":

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

    generate = autoAnimate()



# /Applications/blender-279/Blender.app/Contents/MacOS/blender /Users/ecpc31/Dropbox/Blender/ProgressionClasses/frameRate.blend --background --python /Users/ecpc31/Dropbox/Blender/ProgressionClasses/compositePostHoc.py -- -0.17453292519943295 -0.23561944901923448 -0.8191520442889917,-0.5,0.5735764363510464 4.0 1 0 0 0 1 sandOG tileOG woodOG 0 4 9 1