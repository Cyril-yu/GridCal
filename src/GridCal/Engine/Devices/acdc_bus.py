# This file is part of GridCal.
#
# GridCal is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# GridCal is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with GridCal.  If not, see <http://www.gnu.org/licenses/>.


import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from GridCal.Engine.basic_structures import BusMode
from GridCal.Engine.Devices.meta_devices import EditableDevice, DeviceType, GCProp


class AcDcBus(EditableDevice):
    """
    The Bus object is the container of all the possible devices that can be attached to
    a bus bar or substation. Such objects can be loads, voltage controlled generators,
    static generators, batteries, shunt elements, etc.

    Arguments:

        **name** (str, "Bus"): Name of the bus

        **vnom** (float, 10.0): Nominal voltage in kV

        **vmin** (float, 0.9): Minimum per unit voltage

        **vmax** (float, 1.1): Maximum per unit voltage

        **r_fault** (float, 0.0): Resistance of the fault in per unit (SC only)

        **x_fault** (float, 0.0): Reactance of the fault in per unit (SC only)

        **xpos** (int, 0): X position in pixels (GUI only)

        **ypos** (int, 0): Y position in pixels (GUI only)

        **height** (int, 0): Height of the graphic object (GUI only)

        **width** (int, 0): Width of the graphic object (GUI only)

        **active** (bool, True): Is the bus active?

        **is_slack** (bool, False): Is this bus a slack bus?

        **area** (str, "Default"): Name of the area

        **zone** (str, "Default"): Name of the zone

        **substation** (str, "Default"): Name of the substation

    Additional Properties:

        **Qmin_sum** (float, 0): Minimum reactive power of this bus (inferred from the devices)

        **Qmax_sum** (float, 0): Maximum reactive power of this bus (inferred from the devices)

        **loads** (list, list()): List of loads attached to this bus

        **controlled_generators** (list, list()): List of controlled generators attached to this bus

        **shunts** (list, list()): List of shunts attached to this bus

        **batteries** (list, list()): List of batteries attached to this bus

        **static_generators** (list, list()): List of static generators attached to this bus

        **measurements** (list, list()): List of measurements

    """

    def __init__(self, name="Bus", vnom=400, vmin=0.9, vmax=1.1,
                 xpos=0, ypos=0, height=0, width=0, active=True,
                 area='Default', zone='Default', substation='Default', longitude=0.0, latitude=0.0):

        EditableDevice.__init__(self,
                                name=name,
                                active=active,
                                device_type=DeviceType.BusDevice,
                                editable_headers={'name': GCProp('', str, 'Name of the bus'),
                                                  'active': GCProp('', bool,
                                                                   'Is the bus active? used to disable the bus.'),
                                                  'Vnom': GCProp('kV', float,
                                                                 'Nominal line voltage of the bus.'),
                                                  'Vmin': GCProp('p.u.', float,
                                                                 'Lower range of allowed voltage.'),
                                                  'Vmax': GCProp('p.u.', float,
                                                                 'Higher range of allowed range.'),
                                                  'x': GCProp('px', float, 'x position in pixels.'),
                                                  'y': GCProp('px', float, 'y position in pixels.'),
                                                  'h': GCProp('px', float, 'height of the bus in pixels.'),
                                                  'w': GCProp('px', float, 'Width of the bus in pixels.'),
                                                  'area': GCProp('', str, 'Area of the bus'),
                                                  'zone': GCProp('', str, 'Zone of the bus'),
                                                  'substation': GCProp('', str, 'Substation of the bus.'),
                                                  'longitude': GCProp('deg', float, 'longitude of the bus.'),
                                                  'latitude': GCProp('deg', float, 'latitude of the bus.')},
                                non_editable_attributes=list(),
                                properties_with_profile={'active': 'active_prof'})

        # Nominal voltage (kV)
        self.Vnom = vnom

        # minimum voltage limit
        self.Vmin = vmin

        # maximum voltage limit
        self.Vmax = vmax

        # summation of lower reactive power limits connected
        self.Qmin_sum = 0

        # summation of upper reactive power limits connected
        self.Qmax_sum = 0

        # is the bus active?
        self.active = active

        self.active_prof = None

        self.area = area

        self.zone = zone

        self.substation = substation

        # List of measurements
        self.measurements = list()

        # Bus type
        self.type = BusMode.ACDC

        # position and dimensions
        self.x = xpos
        self.y = ypos
        self.h = height
        self.w = width
        self.longitude = longitude
        self.latitude = latitude

    def add_device(self, device):
        """
        Add device to the bus in the corresponding list
        :param device:
        :return:
        """
        if device.device_type == DeviceType.BatteryDevice:
            self.batteries.append(device)

        elif device.device_type == DeviceType.ShuntDevice:
            self.shunts.append(device)

        elif device.device_type == DeviceType.StaticGeneratorDevice:
            self.static_generators.append(device)

        elif device.device_type == DeviceType.LoadDevice:
            self.loads.append(device)

        elif device.device_type == DeviceType.GeneratorDevice:
            self.controlled_generators.append(device)

        else:
            pass
            # raise Exception('Device type not understood:' + str(device.device_type))

    def determine_bus_type(self):
        """
        Infer the bus type from the devices attached to it
        @return: Nothing
        """

        return self.type

    def copy(self):
        """
        Deep copy of this object
        :return: New instance of this object
        """
        bus = AcDcBus()
        bus.name = self.name

        # Nominal voltage (kV)
        bus.Vnom = self.Vnom

        bus.vmin = self.Vmin

        bus.Vmax = self.Vmax

        bus.Qmin_sum = self.Qmin_sum

        bus.Qmax_sum = self.Qmax_sum

        bus.active = self.active

        # Bus type
        bus.type = self.type

        bus.x = self.x

        bus.y = self.y

        bus.h = self.h

        bus.w = self.w

        bus.area = self.area

        bus.zone = self.zone

        bus.substation = self.substation

        bus.measurements = self.measurements

        # self.graphic_obj = None

        return bus

    def get_json_dict(self, id):
        """
        Return Json-like dictionary
        :return: Dictionary
        """
        return {'id': id,
                'type': 'acdc_bus',
                'phases': 'ps',
                'name': self.name,
                'active': self.active,
                'Vnom': self.Vnom,
                'vmin': self.Vmin,
                'vmax': self.Vmax,
                'x': self.x,
                'y': self.y,
                'h': self.h,
                'w': self.w,
                'area': self.area,
                'zone': self.zone,
                'substation': self.substation}

    def set_state(self, t):
        """
        Set the profiles state of the objects in this bus to the value given in the profiles at the index t
        :param t: index of the profile
        :return: Nothing
        """
        pass

    def retrieve_graphic_position(self):
        """
        Get the position set by the graphic object into this object's variables
        :return: Nothing
        """
        if self.graphic_obj is not None:
            self.x = self.graphic_obj.pos().x()
            self.y = self.graphic_obj.pos().y()
            self.w, self.h = self.graphic_obj.rect().getCoords()[2:4]

    def merge(self, other_bus):
        """
        Add the elements of the "Other bus" to this bus
        :param other_bus: Another instance of Bus
        """
        # List of measurements
        self.measurements += other_bus.measurements.copy()

    def get_coordinates(self):
        """
        Get tuple of the bus coordinates (latitude, longitude)
        """
        return self.latitude, self.longitude
