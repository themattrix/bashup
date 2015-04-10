import pyparsing as pp


NAME = pp.Word(pp.alphas + '_', pp.alphanums + '_')
