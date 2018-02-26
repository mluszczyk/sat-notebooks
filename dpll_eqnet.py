import random
from collections import Counter

from dpll import get_random_ksat, DPLL, SAT
from eqnet_format import dist_to_false, cnf_to_eqnet, ENCODER


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


class MostCommonVarDPLL(DPLL):
    def suggest(self, sat: SAT):
        counter = Counter()
        for clause in sat.clauses:
            for svar in clause:
                counter[svar] += 1
        return counter.most_common(1)[0][0]


class EqnetDPLL(DPLL):
    def suggest(self, sat: SAT):
        best_svar = None
        best_dist = None
        for var in sat.vars:
            for svar in [var, -var]:
                new_sat = sat.set_var(svar)
                if new_sat.is_true():
                    return svar
                if new_sat.is_false():
                    if best_svar is None:
                        best_svar = svar
                    continue
                eqnet_form = cnf_to_eqnet(new_sat.clauses)
                embed = ENCODER.get_encoding(eqnet_form)
                embed_dist = dist_to_false(embed)
                if best_dist is None or embed_dist < best_dist:
                    best_dist = embed_dist
                    best_svar = svar
        return best_svar
