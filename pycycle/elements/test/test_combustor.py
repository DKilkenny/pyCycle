""" Tests the duct component. """

from __future__ import print_function

import unittest
import os

import numpy as np

from openmdao.api import Problem, Group, IndepVarComp

from openmdao.utils.assert_utils import assert_rel_error

from pycycle.elements.combustor import Combustor

from pycycle.elements.test.util import check_element_partials


fpath = os.path.dirname(os.path.realpath(__file__))
ref_data = np.loadtxt(fpath + "/reg_data/combustorJP7.csv",
                      delimiter=",", skiprows=1)

header = ['Fl_I.W', 'Fl_I.Pt', 'Fl_I.Tt', 'Fl_I.ht', 'Fl_I.s', 'Fl_I.MN', 'FAR', 'eff', 'Fl_O.MN',
          'Fl_O.Pt', 'Fl_O.Tt', 'Fl_O.ht', 'Fl_O.s', 'Wfuel', 'Fl_O.Ps', 'Fl_O.Ts', 'Fl_O.hs',
          'Fl_O.rhos', 'Fl_O.gams']

h_map = dict(((v_name, i) for i, v_name in enumerate(header)))


class BurnerTestCase(unittest.TestCase):

    def test_case1(self):

        prob = Problem()
        model = prob.model = Group()

        n_init = np.array([3.23319258e-04, 1.00000000e-10, 1.10131241e-05, 1.00000000e-10,
                           1.63212420e-10, 6.18813039e-09, 1.00000000e-10, 2.69578835e-02,
                           1.00000000e-10, 7.23198770e-03])

        model.add_subsystem(
            'des_var1',
            IndepVarComp(
                'Fl_I:tot:P',
                100.0,
                units='lbf/inch**2'),
            promotes=["*"])
        model.add_subsystem(
            'des_var2',
            IndepVarComp(
                'Fl_I:tot:h',
                100.0,
                units='Btu/lbm'),
            promotes=["*"])
        model.add_subsystem(
            'des_var3',
            IndepVarComp(
                'Fl_I:stat:W',
                100.0,
                units='lbm/s'),
            promotes=["*"])
        model.add_subsystem('des_var4', IndepVarComp('Fl_I:FAR', 0.0), promotes=["*"])
        model.add_subsystem('des_var5', IndepVarComp('MN', 0.5), promotes=["*"])
        model.add_subsystem('des_var6', IndepVarComp('Fl_I:tot:n', n_init), promotes=["*"])

        model.add_subsystem('combustor', Combustor(), promotes=["*"])

        prob.set_solver_print(level=2)
        prob.setup(check=False)

        # 6 cases to check against
        for i, data in enumerate(ref_data):

            # input flowstation
            prob['Fl_I:tot:P'] = data[h_map['Fl_I.Pt']]
            prob['Fl_I:tot:h'] = data[h_map['Fl_I.ht']]
            prob['Fl_I:stat:W'] = data[h_map['Fl_I.W']]
            prob['Fl_I:FAR'] = data[h_map['FAR']]
            prob['MN'] = data[h_map['Fl_O.MN']]

            prob.run_model()

            # check outputs
            tol = 1.0e-2

            npss = data[h_map['Fl_O.Pt']]
            pyc = prob['Fl_O:tot:P']
            rel_err = abs(npss - pyc) / npss
            print('Pt out:', npss, pyc, rel_err)
            self.assertLessEqual(rel_err, tol)

            npss = data[h_map['Fl_O.Tt']]
            pyc = prob['Fl_O:tot:T']
            rel_err = abs(npss - pyc) / npss
            print('Tt out:', npss, pyc, rel_err)
            self.assertLessEqual(rel_err, tol)

            npss = data[h_map['Fl_O.ht']]
            pyc = prob['Fl_O:tot:h']
            rel_err = abs(npss - pyc) / npss
            print('ht out:', npss, pyc, rel_err)
            self.assertLessEqual(rel_err, tol)

            npss = data[h_map['Fl_O.Ps']]
            pyc = prob['Fl_O:stat:P']
            rel_err = abs(npss - pyc) / npss
            print('Ps out:', npss, pyc, rel_err)
            self.assertLessEqual(rel_err, tol)

            npss = data[h_map['Fl_O.Ts']]
            pyc = prob['Fl_O:stat:T']
            rel_err = abs(npss - pyc) / npss
            print('Ts out:', npss, pyc, rel_err)
            self.assertLessEqual(rel_err, tol)

            npss = data[h_map['Wfuel']]
            pyc = prob['Fl_I:stat:W'] * (prob['Fl_I:FAR'])
            rel_err = abs(npss - pyc) / npss
            print('Wfuel:', npss, pyc, rel_err)
            self.assertLessEqual(rel_err, tol)

            print('')

            check_element_partials(self, prob, tol=1e-4)
        # prob.check_partials()

if __name__ == "__main__":
    unittest.main()
