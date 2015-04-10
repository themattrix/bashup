import pyparsing as pp


# Enable memoization to speed up the parser.
pp.ParserElement.enablePackrat()


NAME = pp.Word(pp.alphas + '_', pp.alphanums + '_')
