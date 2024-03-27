# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
#
# Copyright (c) 2024 SweepMe! GmbH (sweep-me.net)
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
# Device: Keithley 4200-SCS
import os

from pysweepme import FolderManager
from pysweepme.EmptyDeviceClass import EmptyDevice

FolderManager.addFolderToPATH()

import importlib

import ProxyClass

importlib.reload(ProxyClass)

# standard path for LPTlib.dll
# If it exists, SweepMe! is running on the instruments PC
RUNNING_ON_4200SCS = os.path.exists(r"C:\s4200\sys\bin\lptlib.dll")

if RUNNING_ON_4200SCS:
    # import LPT library functions
    # import LPT library instrument IDs
    # not available yet -> # from pylptlib import inst
    # import LPT library parameter constants
    from pylptlib import lpt, param


class Device(EmptyDevice):
    """Device class for the Keithley 4200-SCS used as LCRmeter."""

    descprition = "Keithley 4200-SCS LCRmeter"

    def __init__(self) -> None:
        """Initializes the device class."""
        super().__init__()

        self.plottype = [True, True, True, True]  # True to plot data
        self.savetype = [True, True, True, True]  # True to save data

        if not RUNNING_ON_4200SCS:
            self.port_types = ["GPIB", "TCPIP"]
            # needed to make the code working with pysweepme where port_manager is only used from __init__
            self.port_manager = True

        self.port_properties = {
            "EOL": "\r\n",
            "timeout": 10.0,
            "TCPIP_EOLwrite": "\x00",
            "TCPIP_EOLread": "\x00",
        }

        # unclear whether all ranges exist as the documentation does not get clear about it
        self.current_ranges = {
            "Auto": 0,
            # "Fixed 10 mA": 1e-2,
            # "Fixed 1 mA": 1e-3,
            # "Fixed 100 µA": 1e-4,
            # "Fixed 10 µA": 1e-5,
            # "Fixed 1 µA": 1e-6,
            # "Fixed 100 nA": 1e-7,
            # "Fixed 10 nA": 1e-8,
            # "Fixed 1 nA": 1e-9,
            # "Fixed 100 pA": 1e-10,
            # "Fixed 10 pA": 1e-11,
            # "Fixed 1 pA": 1e-12,
            # "Limited 10 mA": 1e-2,
            # "Limited 1 mA": 1e-3,
            # "Limited 100 µA": 1e-4,
            # "Limited 10 µA": 1e-5,
            # "Limited 1 µA": 1e-6,
            # "Limited 100 nA": 1e-7,
            # "Limited 10 nA": 1e-8,
            # "Limited 1 nA": 1e-9,
            # "Limited 100 pA": 1e-10,
            # "Limited 10 pA": 1e-11,
            # "Limited 1 pA": 1e-12,
        }

        self.operating_mode: str = ""
        self.operating_modes = {
            "ZTH": "KI_CVU_TYPE_ZTH",
            "RjX": "KI_CVU_TYPE_RJX",
            "CpGp": "KI_CVU_TYPE_CPGP",
            "CsRs": "KI_CVU_TYPE_CSRS",
            "CpD": "KI_CVU_TYPE_CPD",
            "CsD": "KI_CVU_TYPE_CSD",
            "YTH": "KI_CVU_TYPE_YTH",
        }

        self.speed: str = ""
        self.speeds = {
            "Fast": "KI_CVU_SPEED_FAST",
            "Normal": "KI_CVU_SPEED_NORMAL",
            "Qiet": "KI_CVU_SPEED_QUIET",
            # "Custom"
        }

        # Device specific properties
        self.frequency: int = 0

        self.measured_dc_bias: float = 0.0
        self.measured_frequency: float = 0.0
        self.resistance: float = 0.0
        self.reactance: float = 0.0

        self.bias_mode: str = ""

        self.integration = None
        self.ALC = None
        self.stepmode = None
        self.sweepmode = None
        self.shortname = "Keithley_4200-SCS"

    def find_ports(self) -> list:
        """Finds the available ports for the Keithley 4200-SCS LCRmeter."""
        # TODO: update SweepMe! to allow finding ports next to the automatically found one

        ports = ["LPTlib via xxx.xxx.xxx.xxx"]

        if RUNNING_ON_4200SCS:
            ports.insert(0, "LPTlib control - no port required")

        return ports

    def set_GUIparameter(self) -> dict[str, any]:  # noqa: N802
        """Set initial GUI parameter in SweepMe!."""
        return {
            # "Average": ["1", "2", "4", "8", "16", "32", "64"],  # TODO: check
            "SweepMode": ["None", "Frequency in Hz", "Voltage bias in V", "Voltage level in V"],
            "StepMode": ["None", "Frequency in Hz", "Voltage bias in V", "Voltage level in V"],
            "ValueRMS": 0.02,
            "ValueBias": 0.0,
            "Frequency": 1000.0,
            "Integration": list(self.speeds),
            "TriggerDelay": "0.1",
            "ALC": ["Off"],  # TODO: check
            "Trigger": ["Internal"],
            "Range": list(self.current_ranges),
        }

    def get_GUIparameter(self, parameter: dict) -> None:  # noqa: N802
        """Update parameter from SweepMe! GUI."""
        self.port_string = parameter["Port"]
        # TODO: Where does the card id come from?
        self.card_id = 0

        # Copied from LCR example
        self.sweepmode = parameter["SweepMode"]
        self.stepmode = parameter["StepMode"]

        self.ValueRMS = float(parameter["ValueRMS"])
        self.ValueBias = float(parameter["ValueBias"])

        self.frequency = float(parameter["Frequency"])

        self.integration = self.speeds[parameter["Integration"]]

        self.delay = float(parameter["TriggerDelay"])

        self.trigger_type = parameter["Trigger"]  # TODO: check
        self.range = self.current_ranges[parameter["Range"]]

        # Only use Resistance and reactance measurement
        self.operating_mode = self.operating_modes["RjX"]

    def handle_measurement_mode(self) -> None:
        """Extract correct measurement mode and set variables and units accordingly."""
        if self.stepmode != "None" and self.sweepmode == self.stepmode:
            msg = "Sweep and step mode cannot be the same."
            raise Exception(msg)

        variable = "Voltage level" if self.sweepmode == "Voltage level in V" else "Voltage bias"

        self.variables = ["R", "X", "Frequency", variable]
        self.units = ["Ohm", "Ohm", "Hz", "V"]

    def connect(self) -> None:
        """Connect to the Keithley 4200-SCS LCRmeter or the proxy."""
        if self.port_manager:
            self.command_set = "US"  # "US" user mode, "LPTlib", # check manual p. 677/1510

            # very important, triggers a (DCL) in KXCI, seems to be essential to read correct values
            self.port.port.clear()

        else:
            self.command_set = "LPTlib"  # "US" user mode, "LPTlib", # check manual p. 677/1510

            if not RUNNING_ON_4200SCS:
                # overwriting the communication classes with Proxy classes
                tcp_ip_port = self.port_string[11:].strip()  # removing "LPTlib via "
                tcp_ip_port_splitted = tcp_ip_port.split(":")  # in case a port is given
                tcp_ip = tcp_ip_port_splitted[0]

                tcp_port = int(tcp_ip_port_splitted[1]) if len(tcp_ip_port_splitted) == 2 else 8888

                self.lpt = ProxyClass.Proxy(tcp_ip, tcp_port, "lpt")
                # not supported yet with pylptlib -> # self.inst = Proxy(tcp_ip, tcp_port, "inst")
                self.param = ProxyClass.Proxy(tcp_ip, tcp_port, "param")

            else:
                # we directly use pylptlib
                self.lpt = lpt
                # not supported yet with pylptlib -> # self.inst = inst
                self.param = param

            self.lpt.initialize()

            self.card_id = self.lpt.getinstid(self.card_name)

    def initialize(self) -> None:
        """Initialize the Keithley 4200-SCS LCRmeter or the proxy."""
        self.handle_measurement_mode()
        self.identifier = "Keithley_4200-SCS_" + self.port_string

        if self.identifier not in self.device_communication:
            if self.command_set == "LPTlib":
                self.lpt.tstsel(1)
                self.lpt.devint()  # This command resets all active instruments in the system to their default states.

            elif self.command_set == "US":
                # TODO: Check
                if self.current_range != "Auto":
                    msg = "When using KXCI only Auto current range is supported."
                    raise Exception(msg)

                # TODO: Check if needed, retrieve options?
                self.clear_buffer()
                self.set_to_4200()
                self.set_command_mode("US")
                self.set_data_service()
                self.set_resolution(7)

            self.device_communication[self.identifier] = {}  # dictionary that can be filled with further information

    def deinitialize(self) -> None:
        """Reset device and close connection."""
        if self.identifier in self.device_communication:
            if self.command_set == "LPTlib":
                self.lpt.devint()  # restores default values
                self.lpt.tstdsl()  # TODO: not implemented yet

            del self.device_communication[self.identifier]

    def configure(self) -> None:
        """Set bias and measurement parameters with start values from GUI."""
        self.set_ac_frequency(self.frequency)
        self.set_delay(self.delay)

        self.set_dc_bias(self.ValueBias)
        self.set_ac_voltage(self.ValueRMS)

        self.set_measure_range()

    def unconfigure(self) -> None:
        """Reset device."""
        self.reset_cvu()

    def apply(self) -> None:
        """Apply settings."""
        if self.sweepmode != "None":
            sweep_value = float(self.value)
            self.handle_set_value(self.sweepmode, sweep_value)

        if self.stepmode != "None":
            step_value = float(self.stepvalue)
            self.handle_set_value(self.stepmode, step_value)

    def handle_set_value(self, mode: str, value: float) -> None:
        """Set value for sweep or step mode."""
        if mode == "Voltage bias in V":
            self.set_dc_bias(value)

        elif mode == "Voltage level in V":
            self.set_ac_voltage(value)

        elif mode == "Frequency in Hz":
            self.set_ac_frequency(value)

    def measure(self) -> None:
        """Retrieve Impedance results from device."""
        # Only measurement mode RjX is used
        self.resistance, self.reactance = self.measure_impedance()
        self.measured_frequency = self.measure_frequency()

        # TODO: What about voltage level?
        self.measured_dc_bias = self.measure_dc_bias()

    def call(self) -> list[float]:
        """Return ["R", "X", "Frequency", "Voltage bias" or "Voltage level"]."""
        return [self.resistance, self.reactance, self.measured_frequency, self.measured_dc_bias]

    """ here, convenience functions start """
    def clear_buffer(self) -> None:
        """Clear buffer."""
        self.port.write("BC")

        if self.port_string.startswith("TCPIP"):
            self.port.read()

    def set_to_4200(self) -> None:
        """Set to 4200 mode for this session."""
        self.port.write("EM 1,0")

        if self.port_string.startswith("TCPIP"):
            self.port.read()

    def set_command_mode(self, mode: str) -> None:
        """Set mode as US (user mode) or UL (usrlib)."""
        self.port.write(f"{mode}")

        if self.port_string.startswith("TCPIP"):
            self.port.read()

    def set_data_service(self) -> None:
        """Set data service request."""
        if self.command_set == "US":
            self.port.write("DR0")

        if self.port_string.startswith("TCPIP"):
            self.port.read()

    def set_resolution(self, resolution: int) -> None:
        """Set resolution for measurement."""
        if self.command_set == "US":
            self.port.write(f"RS {resolution}")

        if self.port_string.startswith("TCPIP"):
            self.port.read()

    """ here wrapped functions start """

    def set_dc_bias(self, dc_bias: float) -> None:
        """Set DC bias in Volt."""
        self.lpt.forcev(self.card_id, dc_bias)

    def set_ac_voltage(self, ac_voltage: float) -> None:
        """Set AC voltage in Volt."""
        self.lpt.setlevel(self.card_id, ac_voltage)

    def set_ac_frequency(self, ac_frequency: float) -> None:
        """Set AC frequency in Hz."""
        self.lpt.setfreq(self.card_id, ac_frequency)

    def set_delay(self, delay: float) -> None:
        """Set delay in seconds."""
        self.lpt.rdelay(delay)

    def set_measure_range(self) -> None:
        """Set measure range."""
        if self.range == 0:
            self.lpt.setauto(self.card_id)

    def measure_impedance(self) -> list[float]:
        """Measure impedance."""
        result1, result2 = self.lpt.measz(self.card_id, self.operating_mode, self.speed)
        return [result1, result2]

    def measure_frequency(self) -> float:
        """Measure frequency sourced during single measurement."""
        return self.lpt.measf(self.card_id)

    def measure_dc_bias(self) -> float:
        """Measure DC bias sourced during single measurement."""
        return self.lpt.measv(self.card_id)

    def reset_cvu(self) -> None:
        """Reset CVU."""
        self.lpt.devint()