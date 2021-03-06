from typing import List

import numpy
import theano
from data.tree import Node
from encoders.baseencoder import AbstractEncoder

from dpll import get_random_ksat, DPLL


def variable_to_tree(num: int, parent):
    letter = chr(ord('a') + abs(num) - 1)
    assert 'a' <= letter <= 'z'

    if num >= 0:
        return Node(letter, (), letter, parent)
    else:
        not_node = Node('Not', ('child',), parent=parent)
        literal_node = Node(letter, (), letter, not_node)
        not_node.set_children_for_property('child', [literal_node])
        return not_node


def clause_to_tree(clause: List[int], parent, log_depth=False):
    assert clause
    clause = list(clause)

    if len(clause) == 1:
        return variable_to_tree(clause[0], parent)
    else:
        border = int(len(clause) / 2) if log_depth else 1
        or_node = Node('Or', ('left', 'right'), parent=parent)
        left = clause_to_tree(clause[:border], or_node, log_depth)
        or_node.set_children_for_property('left', [left])
        right = clause_to_tree(clause[border:], or_node, log_depth)
        or_node.set_children_for_property('right', [right])
        return or_node


def cnf_to_eqnet(clauses, parent=None, log_depth=False):
    assert clauses

    if parent is None:
        start = Node("Start", ("child",))
        cnf_node = cnf_to_eqnet(clauses, start, log_depth)
        start.set_children_for_property("child", [cnf_node])
        return list('whatever'), start

    if len(clauses) == 1:
        return clause_to_tree(clauses[0], parent, log_depth)
    else:
        border = int(len(clauses) / 2) if log_depth else 1
        and_node = Node('And', ('left', 'right'), parent=parent)
        left = cnf_to_eqnet(clauses[:border], and_node, log_depth)
        and_node.set_children_for_property('left', [left])
        right = cnf_to_eqnet(clauses[border:], and_node, log_depth)
        and_node.set_children_for_property('right', [right])
        return and_node


def l2(x, y):
    return numpy.sqrt(numpy.sum((x - y) ** 2))


def mean(x):
    return sum(x)/len(x)


def stdev(x):
    return (sum(y**2 for y in x)/len(x) - mean(x)**2)**0.5


ENCODER_PKL = "models/rnnsupervisedencoder-largeSimpleBoolean5.pkl"


def get_encoder():
    return AbstractEncoder.load(ENCODER_PKL)


def get_false_encoding(encoder):
    false_eqnet_form = cnf_to_eqnet([[1], [-1]])
    return encoder.get_encoding(false_eqnet_form)


def main():
    print(theano.__version__)
    encoder = get_encoder()

    false_encoding = get_false_encoding(encoder)

    trues = []
    falses = []
    for i in range(1000):
        rsat = get_random_ksat(3, 3, 20)
        clauses = [list(clause) for clause in rsat.clauses]
        eqnet_form = cnf_to_eqnet(clauses)
        encoding = encoder.get_encoding(eqnet_form)
        dist = l2(encoding, false_encoding)
        if DPLL().run(rsat):
            trues.append(dist)
        else:
            falses.append(dist)
    print("#Trues: {}; avg dist: {}; stdev dist: {}".format(
        len(trues), mean(trues), stdev(trues)))
    print("#Falses: {}; avg dist: {}; stdev dist: {}".format(
        len(falses), mean(falses), stdev(falses)))


if __name__ == "__main__":
    main()
