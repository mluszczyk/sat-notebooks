from typing import List

from data.tree import Node


def variable_to_tree(num: int, parent):
    letter = chr(ord('a') + abs(num) - 1)
    assert 'a' <= letter <= 'z'

    if letter >= 0:
        return Node(letter, (), letter, parent)
    else:
        not_node = Node('Not({})'.format(letter), ('child',), parent)
        literal_node = Node(letter, (), letter, not_node)
        not_node.set_children_for_property('child', [literal_node])
        return not_node

def fold_formula(list_: List, parent):
    return ...

def clause_to_tree(clause: List[int], parent):
    assert clause

    if len(clause) == 1:
        return variable_to_tree(clause[0], parent)
    else:
        or_node = Node('Or(...)', ('left', 'right'), parent)
        left = variable_to_tree(clause[0], or_node)
        or_node.set_children_for_property('left', [left])
        right = clause_to_tree(clause[1:], or_node)
        or_node.set_children_for_property('right', [right])
        return or_node


def cnf_to_eqnet(clauses):
    pass