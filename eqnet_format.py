from typing import List

import theano
from data.tree import Node
from encoders.baseencoder import AbstractEncoder

from dpll import get_random_ksat, DPLL

ENCODER_PKL = "models/rnnsupervisedencoder-largeSimpleBoolean5.pkl"


def variable_to_tree(num: int, parent):
    letter = chr(ord('a') + abs(num) - 1)
    assert 'a' <= letter <= 'z'

    if num >= 0:
        return Node(letter, (), letter, parent)
    else:
        not_node = Node('Not({})'.format(letter), ('child',), parent=parent)
        literal_node = Node(letter, (), letter, not_node)
        not_node.set_children_for_property('child', [literal_node])
        return not_node


def clause_to_tree(clause: List[int], parent):
    assert clause

    if len(clause) == 1:
        return variable_to_tree(clause[0], parent)
    else:
        or_node = Node('Or(...)', ('left', 'right'), parent=parent)
        left = variable_to_tree(clause[0], or_node)
        or_node.set_children_for_property('left', [left])
        right = clause_to_tree(clause[1:], or_node)
        or_node.set_children_for_property('right', [right])
        return or_node


def cnf_to_eqnet(clauses, parent=None):
    assert clauses

    if parent is None:
        start = Node("Start", ("child",))
        cnf_node = cnf_to_eqnet(clauses, start)
        start.set_children_for_property("child", [cnf_node])
        return list('whatever'), start

    if len(clauses) == 1:
        return clause_to_tree(clauses[0], parent)
    else:
        and_node = Node('And(...)', ('left', 'right'), parent=parent)
        left = clause_to_tree(clauses[0], and_node)
        and_node.set_children_for_property('left', [left])
        right = cnf_to_eqnet(clauses[1:], and_node)
        and_node.set_children_for_property('right', [right])
        return and_node


def main():
    print(theano.__version__)
    rsat = get_random_ksat(2, 4, 2)
    print(rsat)
    print(DPLL().run(rsat))
    clauses = [list(clause) for clause in rsat.clauses]
    eqnet_form = cnf_to_eqnet(clauses)
    print(eqnet_form)

    encoder = AbstractEncoder.load(ENCODER_PKL)
    encoding = encoder.get_encoding(eqnet_form)
    print(encoding)


if __name__ == "__main__":
    main()
