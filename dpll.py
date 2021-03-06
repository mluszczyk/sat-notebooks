import random
from typing import List, Tuple, Set
from random import randint, choice

from sympy.logic import simplify_logic
from sympy.parsing.sympy_parser import parse_expr


def get_random_ksat(k, n, m):
    """returns k-SAT with max n variables and m clauses"""
    clauses = []
    for i in range(m):
        clause = []
        for j in range(k):
            var = randint(1, n)
            sign = choice([1, -1])
            svar = sign * var
            clause.append(svar)
        clauses.append(clause)
    return SAT(clauses)


def get_random_ksats(sample_number, clause_size, variable_number,
                     clause_number):
    rsats = [get_random_ksat(clause_size, variable_number,
                             random.randint(1, clause_number))
             for _ in range(sample_number)]
    return rsats


class SAT(object):
    def __init__(self, clauses: List[List[int]]):
        clauses = tuple(tuple(c) for c in clauses)
        if clauses:
            svars = set(abs(x)
                        for clause in clauses
                        for x in clause)
        else:
            svars = set()

        assert all((isinstance(x, int) and x > 0) for x in svars)

        assert all(all((abs(x) in svars) for x in c) for c in clauses)

        self.vars = svars
        self.clauses = clauses

    def get_token_string(self):
        def num_to_letter(num):
            assert num <= 25
            return chr(num-1+ord('a'))
        tokens = []
        for clause in self.clauses:
            tokens.append('(')
            for var in clause:
                if var < 0:
                    tokens.append('~')
                tokens.append(num_to_letter(abs(var)))
                tokens.append('|')
            tokens.pop()
            tokens.append(')')
            tokens.append('&')
        tokens.pop()
        return ''.join(tokens)

    def simplified(self):
        return simplify_logic(parse_expr(self.get_token_string()))

    def set_var(self, v):
        av = abs(v)
        assert av in self.vars
        new_clauses = []
        existed = False
        for c in self.clauses:
            if v in c:
                existed = True
                continue
            if -v in c:
                existed = True
                c = set(c)
                c.remove(-v)
            new_clauses.append(c)
        if not existed:
            raise ValueError("Variable didn't exist.")
        return SAT(new_clauses)

    def is_true(self):
        return not self.clauses

    def is_false(self):
        return any(not c for c in self.clauses)

    def __str__(self):
        prefix = ("TRUE:" if self.is_true() else
                  ("FALSE:" if self.is_false() else "???:"))
        return prefix + str(self.clauses)

    def __hash__(self):
        return hash(self.clauses)

    def __eq__(self, other):
        return self.clauses == other.clauses


class DPLL(object):
    def __init__(self):
        self.number_of_runs = 0

    def run(self, sat: SAT):
        assert isinstance(sat, SAT)
        self.number_of_runs += 1

        if sat.is_true():
            return []
        elif sat.is_false():
            return None

        sug_var = self.suggest(sat)
        sug_sat = sat.set_var(sug_var)

        sug_res = self.run(sug_sat)
        if sug_res is not None:
            return [sug_var] + sug_res

        not_sug_sat = sat.set_var(-sug_var)
        not_sug_res = self.run(not_sug_sat)
        if not_sug_res is not None:
            return [-sug_var] + not_sug_res
        return None

    def suggest(self, sat):
        return sat.vars[0]


def main():
    s = SAT([
        [1, 2],
        [-2, 3],
        [-3],
        [3],
    ])
    print(s)
    print(DPLL().run(s))

    rsat = get_random_ksat(3, 4, 20)
    print(rsat)
    print(DPLL().run(rsat))
    print(rsat.simplified())


if __name__ == "__main__":
    main()
