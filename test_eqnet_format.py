from unittest import TestCase

from dpll import SAT
from eqnet_format import cnf_to_eqnet


class TestEqnetFormat(TestCase):
    def test(self):
        print(str(cnf_to_eqnet([SAT([[1, 2, 3], [-1, -2]])])))
