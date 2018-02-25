from typing import List, Tuple, Set


class SAT(object):
    def __init__(self, clauses: List[Set[int]]):
        clauses = [set(c) for c in clauses]
        if clauses:
            svars = [abs(x) for x in set.union(*clauses)]
        else:
            svars = set()

        assert all((isinstance(x, int) and x > 0) for x in svars)

        assert all(all((abs(x) in svars) for x in c) for c in clauses)

        self.vars = svars
        self.clauses = clauses

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


class DPLL(object):
    def run(self, sat: SAT):
        assert isinstance(sat, SAT)

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


if __name__ == "__main__":
    main()