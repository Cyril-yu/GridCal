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
import pandas as pd
from matplotlib import pyplot as plt
from GridCal.Engine.Devices.meta_devices import EditableDevice, DeviceType, GCProp


class AcDcConverter(EditableDevice):

    def __init__(self, name, type_dc, type_ac, P_g, Q_g, Vtar, rtf, xtf, bf, rc, xc, basekVac,
                 Vmmax, Vmmin, Imax, active, LossA, LossB, LossCrec, LossCinv):
        """

        :param name:
        :param type_dc:
        :param type_ac:
        :param P_g:
        :param Q_g:
        :param Vtar:
        :param rtf: transformer series resistance
        :param xtf: transformer series reactance
        :param bf: filter susceptance
        :param rc: phase resistance
        :param xc: phase reactance
        :param basekVac:
        :param Vmmax:
        :param Vmmin:
        :param Imax:
        :param active:
        :param LossA:
        :param LossB:
        :param LossCrec:
        :param LossCinv:
        """

        EditableDevice.__init__(self,
                                name=name,
                                active=active,
                                device_type=DeviceType.LoadDevice,
                                editable_headers={'name': GCProp('', str, 'Load name'),
                                                  'bus': GCProp('', DeviceType.BusDevice, 'Connection bus name'),
                                                  'active': GCProp('', bool, 'Is the load active?'),
                                                  'P': GCProp('MW', float, 'Active power'),
                                                  'Q': GCProp('MVAr', float, 'Reactive power'),
                                                  'Ir': GCProp('MW', float,
                                                               'Active power of the current component at V=1.0 p.u.'),
                                                  'Ii': GCProp('MVAr', float,
                                                               'Reactive power of the current component at V=1.0 p.u.'),
                                                  'G': GCProp('MW', float,
                                                              'Active power of the impedance component at V=1.0 p.u.'),
                                                  'B': GCProp('MVAr', float,
                                                              'Reactive power of the impedance component at V=1.0 p.u.'),
                                                  'mttf': GCProp('h', float, 'Mean time to failure'),
                                                  'mttr': GCProp('h', float, 'Mean time to recovery'),
                                                  'Cost': GCProp('e/MWh', float,
                                                                 'Cost of not served energy. Used in OPF.')},
                                non_editable_attributes=list(),
                                properties_with_profile={'active': 'active_prof',
                                                         'P': 'P_prof',
                                                         'Q': 'Q_prof',
                                                         'Ir': 'Ir_prof',
                                                         'Ii': 'Ii_prof',
                                                         'G': 'G_prof',
                                                         'B': 'B_prof',
                                                         'Cost': 'Cost_prof'})

        self.bus = None

        self.type_dc = type_dc

        self.type_ac = type_ac

        self.Vtar = Vtar

        self.rtf = rtf

        self.xtf = xtf

        self.bf = bf

        self.rc = rc

        self.xc = xc

        self.basekVac = basekVac

        self.Vmmax = Vmmax

        self.Vmmin = Vmmin

        self.Imax = Imax

        self.active = active

        self.LossA = LossA

        self.LossB = LossB

        self.LossCrec = LossCrec

        self.LossCinv = LossCinv

        self.active_prof = None

    def copy(self):

        load = AcDcConverter()

        load.name = self.name

        # Impedance (MVA)
        load.G = self.G
        load.B = self.B

        # Current (MVA)
        load.Ir = self.Ir
        load.Ii = self.Ii

        # Power (MVA)
        load.P = self.P
        load.Q = self.Q

        # Impedance (MVA)
        load.G_prof = self.G_prof
        load.B_prof = self.B_prof

        # Current (MVA)
        load.Ir_prof = self.Ir_prof
        load.Ii_prof = self.Ii_prof

        # Power (MVA)
        load.P_prof = self.P_prof
        load.Q_prof = self.Q_prof

        load.mttf = self.mttf

        load.mttr = self.mttr

        return load

    def get_json_dict(self, id, bus_dict):
        """
        Get json dictionary
        :param id: ID: Id for this object
        :param bus_dict: Dictionary of buses [object] -> ID
        :return:
        """
        return {'id': id,
                'type': 'load',
                'phases': 'ps',
                'name': self.name,
                'bus': bus_dict[self.bus],
                'active': self.active,
                'G': self.G,
                'B': self.B,
                'Ir': self.Ir,
                'Ii': self.Ii,
                'P': self.P,
                'Q': self.Q}

