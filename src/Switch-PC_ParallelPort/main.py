# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
# 
# Copyright (c) 2018-2019 Axel Fischer (sweep-me.net)
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


# SweepMe! device class
# Type: Switch
# Device: PC ParallelPort


from EmptyDeviceClass import EmptyDevice
import ctypes
import os

libpath = os.path.dirname(__file__) + os.sep + 'libs'

if not libpath in os.environ["PATH"]:
    os.environ["PATH"] = os.environ["PATH"] + ";" + libpath 
    
class Device(EmptyDevice):

    description = """
                  Sweep value must be an integer between 0 and 255, corresponding to sum of 2^i where i is pin 0 to 7
                  """

    def __init__(self):
        EmptyDevice.__init__(self)
        
        self.shortname = "ParallelPort"
        
        self.variables = ["Configuration"]
        self.units = [""]
        self.plottype = [False]  # True to plot data
        self.savetype = [True]  # True to save data
  
        self.p = ctypes.windll.inpout32 # configure parallel port

        
    def set_GUIparameter(self):
        
        GUIparameter = {
                        "SweepMode" : ["Configuration"],
                        }
                        
        return GUIparameter
        
    def find_Ports(self):
        
        return ["Parallel Port"]
        
        
    def initialize(self):
        self.p.Out32(0x378,0)
        
    def deinitialize(self):
        self.p.Out32(0x378,0)
        
    def apply(self):
        self.value = int(self.value)
        self.p.Out32(0x378, self.value)
        
    def call(self):
        return self.value