import pysweepme  # use "pip install pysweepme" in command line to install
import os
import sys
import time


# the name of the driver where this example file is in
driver_name = os.path.dirname(os.path.dirname((os.path.abspath(__file__)))).split(os.sep)[-1]

# the path of the driver where this example file is in
driver_path = os.path.dirname((os.path.dirname(os.path.dirname((os.path.abspath(__file__))))))

# port_string = "GPIB0::1::INSTR"  # please change GPIB port
port_string = "GPIB3::6::INSTR"

uf = pysweepme.get_driver(driver_name, driver_path, port_string)

uf.connect()  # needed to create an AccretechProber instance inside the driver instance

uf.print_info()  # prints out general static information

uf.print_status()  # prints out the current system status

prober_status = uf.prober.request_prober_status()
if prober_status != "I":
    raise Exception("Please make sure that the prober is in the state I: "
                    "'Waiting for lot process to start' before you try again.")

dies_to_probe = uf.read_controlmap("test.MDF")  # please enter a path to your control map MDF file
# print("Control map with PROB dies:", dies_to_probe)

cassette_status = uf.prober.request_cassette_status()
if cassette_status == "000000":
    # Wafer sensing "jw" command
    uf.prober.sense_wafers()

# Get cassettes and wafers
wafer_status = uf.prober.request_wafer_status()
wafer_list = uf.prober.get_waferlist_from_status(wafer_status)  # a list of tuples containing cassette and wafer id

if len(wafer_list) == 0:
    uf.prober.sense_wafers()  # Wafer sensing "jw" command

    wafer_status = uf.prober.request_wafer_status()
    wafer_list = uf.prober.get_waferlist_from_status(wafer_status)  # a list of tuples containing cassette and wafer id

    if len(wafer_list) == 0:
        raise Exception("Empty wafer list, please make sure the cassette is filled and "
                        "you have sensed the wafer before you try again.")

for wafer in wafer_list[:2]:

    uf.prober.load_specified_wafer(*wafer)  # *wafer unpacks cassette id and wafer id from tuple

    uf.print_status()

    if not uf.prober.is_chuck_contacted():
        uf.prober.z_up()

    for die in dies_to_probe[:3]:  # first 3 dies for testing purposes
        x, y = map(int, die.split(","))  # splitting of the die x,y indices from string
        uf.prober.move_specified_die(x, y)  # die at index x,y

        # Check whether dies are correct
        uf.print_die_info()

        time.sleep(1)  # a bit time to follow the process

    # Chuck down
    uf.prober.z_down()

uf.print_status()

# Terminating the lot process will also bring the last wafer on chuck back to the cassette
uf.prober.terminate_lot_process_immediately()

uf.print_status()
