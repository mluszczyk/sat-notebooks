import random
import sys

from typing import Sequence
from collections import defaultdict, OrderedDict, namedtuple
from sympy.logic import simplify_logic
from sympy.parsing.sympy_parser import parse_expr
from tqdm import tqdm

from data.datasetgenerator import save_result_as_gzipped_json
from data.tree import Node
from data.synthetic.boolexpressions import convert_to_dict, to_token_sequence

from eqnet_format import cnf_to_eqnet


SYMBOLS = [("&", 2), ("|", 2), ("~", 1)] * 4 + [(None, 0)]

BINARY_NONTERMINALS = {'&': 'And', '|': 'Or'}


class TreeNode(namedtuple('TreeNode', ["symbol", "children"])):
    def to_eqnet(self, parent=None):
        if parent is None:
            parent = Node('Start', ('child',))
            child = self.to_eqnet(parent)
            parent.set_children_for_property('child', (child,))
            return parent

        if type(self.symbol) == int:
            return Node(chr(ord('a') - 1 + self.symbol), (), parent=parent)

        if self.symbol in BINARY_NONTERMINALS.keys():
            node = Node(BINARY_NONTERMINALS[self.symbol], ('left', 'right'), parent=parent)
            left = self.children[0].to_eqnet(node)
            right = self.children[1].to_eqnet(node)
            node.set_children_for_property('left', (left,))
            node.set_children_for_property('right', (right,))
            return node

        if self.symbol == '~':
            node = Node('Not', ('child',), parent=parent)
            child = self.children[0].to_eqnet(node)
            node.set_children_for_property('child', (child,))
            return node

        assert False, "unknown symbol '{}'".format(self.symbol)

    def size(self):
        return 1 + sum(child.size() for child in self.children)

    def depth(self):
        return 1 + max((child.depth() for child in self.children), default=0)


def generate_random_tree(tree_max_size: int, variables: Sequence[str]):
    symbol, degree = random.choice(SYMBOLS)

    if tree_max_size <= 1 or symbol is None:
        return TreeNode(random.choice(variables), ())
    return TreeNode(
        symbol,
        tuple(generate_random_tree((tree_max_size - 1) // degree, variables) for _ in range(degree)))


def get_random_trees(sample_number, tree_max_size, variable_number):
    for _ in range(sample_number):
        yield generate_random_tree(random.randint(1, tree_max_size),
                                   variables=list(range(1, variable_number + 1)))


def main(filename, sample_number, tree_max_size, variable_number,
         min_class_size):
    synthesized = defaultdict(lambda: set())

    formula_generator = get_random_trees(sample_number, tree_max_size,
                                         variable_number)
    for i, tree in tqdm(list(enumerate(formula_generator))):
        eqnet_tree = tree.to_eqnet()
        simplified_str = str(simplify_logic(parse_expr(''.join(to_token_sequence(eqnet_tree, []))), form='dnf'))
        synthesized[simplified_str].add(tree)

    print("Number of formulas after filtering",
          sum(len(sats) for sats in synthesized.values()))

    synthesized_expressions = {key: [tree.to_eqnet() for tree in trees]
                               for key, trees in synthesized.items()}

    print("Number of classes before filtering", len(synthesized_expressions))
    synthesized_expressions = {
        key: trees for key, trees in synthesized_expressions.items()
        if len(trees) >= min_class_size}
    print("Number of classes after filtering", len(synthesized_expressions))

    print("Done.")

    def save_to_json_gz(data, filename):
        converted_to_standard_format = {}
        for n, all_expressions in data.items():
            expression_dicts = [dict(Tokens=list("whatever"), Tree=convert_to_dict(expr))
                                for expr in all_expressions]
            converted_to_standard_format[n] = dict(Original=expression_dicts[0],
                                                   Noise=expression_dicts[1:])

        save_result_as_gzipped_json(filename, converted_to_standard_format)

    save_to_json_gz(synthesized_expressions, filename + ".json.gz")


if __name__ == "__main__":
    main(sys.argv[1], *map(int, sys.argv[2:]))
