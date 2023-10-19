# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.

# MIT License

# Copyright (c) 2018-2019 Axel Fischer (sweep-me.net)

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# SweepMe! device class
# Type: Logger
# Device: Minolta CS100A


import time
from EmptyDeviceClass import EmptyDevice

class Device(EmptyDevice):

    description =   """
                    <p>In order to use the remote mode, do the following steps</p>
                    <ol>
                    <li>switch the camera off</li>
                    <li>switch the camera on while pressing the white button labeled "F"</li>
                    <li>If a 'C' appears on the display, you are ready to go.</li>
                    </ol>
                    <p>Properties:</p>
                    <ul>
                    <li>reads out Luminance, CIEx, and CIEy</li>
                    <li>time to read is typically between 1-2 s</li>
                    </ul>
                    """

    def __init__(self):
    
        EmptyDevice.__init__(self)
        
        self.shortname = "CS100A"
        
        self.port_manager = True
        self.port_types = ["COM"]
        self.port_properties = {    "timeout": 3,
                                    "delay": 0.01,
                                    "baudrate": 4800,
                                    "bytesize": 7,
                                    "stopbits": 2,
                                    "parity": 'E',
                                    "EOL": '\r\n',
                                    "rts": True,
                                    "dtr": True, 
                                    }
        
        self.variables = ["Luminance", "CIEx", "CIEy"]
        self.units = ["cd/m^2", "", ""]

        
    def measure(self):
        pass
        
    def call(self):
    
        x = [float('nan'),float('nan'),float('nan'),float('nan')]
        
        for i in range(5):

            self.port.port.flushOutput()
            self.port.port.flushInput()
            self.port.write("MES")
            y = self.port.read().replace(' ','').split(",")

            if len(y) == 4:
                x = y
                break
                
        return [float(x[1]), float(x[2]), float(x[3])] # Luminance, CIEx, CIEy