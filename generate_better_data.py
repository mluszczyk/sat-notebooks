import random
import sys

from collections import defaultdict, OrderedDict
from sympy.logic import simplify_logic
from sympy.parsing.sympy_parser import parse_expr
from tqdm import tqdm

from data.datasetgenerator import save_result_as_gzipped_json
from data.tree import Node
from data.synthetic.boolexpressions import convert_to_dict

from dpll import get_random_ksats
from eqnet_format import cnf_to_eqnet


def main(filename, sample_number, clause_size, variable_number, clause_number):
    synthesized_expressions = defaultdict(lambda: list())

    formula_generator = get_random_ksats(sample_number, clause_size,
                                         variable_number, clause_number)
    for i, sat in tqdm(list(enumerate(formula_generator))):
        tree_form = cnf_to_eqnet(sat.clauses)

        expression = sat.simplified()
        expression_str = str(expression)
        synthesized_expressions[expression_str].append(tree_form)
    print(synthesized_expressions)
    print("Done.")

    def save_to_json_gz(data, filename):
        converted_to_standard_format = {}
        for n, all_expressions in data.items():
            all_expressions = all_expressions[0]
            expression_dicts = [dict(Tokens=expr[0], Tree=convert_to_dict(expr[1]))
                                for expr in all_expressions]
            converted_to_standard_format[n] = dict(Original=expression_dicts[0],
                                                   Noise=expression_dicts[1:])

        save_result_as_gzipped_json(filename, converted_to_standard_format)

    save_to_json_gz(synthesized_expressions, filename + ".json.gz")


if __name__ == "__main__":
    main(sys.argv[1], *map(int, sys.argv[2:]))
