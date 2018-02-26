import random

from dpll import get_random_ksat, DPLL, SAT


class RandomVarDPLL(DPLL):
    def suggest(self, sat: SAT):
        var = random.choice(sat.vars)
        var *= random.choice([-1, 1])
        return var


class RandomClauseDPLL(DPLL):
    def suggest(self, sat: SAT):
        clause = random.choice(sat.clauses)
        var = random.choice(list(clause))
        # We don't randomize a sign, it's on purpose.
        return var


class EqnetDPLL(DPLL):
    def suggest(self):
        pass
