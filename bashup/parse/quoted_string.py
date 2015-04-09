import pyparsing as pp


def get_single_quoted_string():
    return pp.QuotedString("'", multiline=True, unquoteResults=False)


# TODO: test/implement get_double_quoted_string()
# s = '''
# "hello, $(echo "hi there,  `echo "what"`  $SIMPLE
# ${COMPLEX##"${what:$(ls)}"} $(echo "boo") $(date)")
# ) \\\\\\"bill\\wat\\""
# '''
#
# name = pp.Word(alphas + '_', alphanums + '_')
# capturingSubshell = pp.Forward()
# doubleQuotedString = pp.Forward()
# variable = pp.Forward()
# stringComponent = (
#     pp.Literal('\\"')
#     | pp.Literal('\\$')
#     | pp.Literal('\\')
#     | pp.Word(pp.printables + '\n\t ', excludeChars='\\"$`')
#     | variable
#     | capturingSubshell)
# parenSubshellComponent = (
#     pp.Word(pp.printables + '\n\t ', excludeChars=')"')
#     | doubleQuotedString)
# backtickSubshellComponent = (
#     pp.Word(pp.printables + '\n\t ', excludeChars='`"')
#     | doubleQuotedString)
# variableComponent = (
#     pp.Word(pp.printables + '\n\t ', excludeChars='}"')
#     | doubleQuotedString)
# simpleVariable = '$' + name
# complexVariable = '${' + pp.ZeroOrMore(variableComponent) + '}'
# variable << (simpleVariable | complexVariable)
# parenSubshell = '$(' + pp.ZeroOrMore(parenSubshellComponent) + ')'
# backtickSubshell = '`' + pp.ZeroOrMore(backtickSubshellComponent) + '`'
# capturingSubshell << (parenSubshell | backtickSubshell)
# doubleQuotedString << pp.Combine('"' + pp.ZeroOrMore(stringComponent) + '"')
#
# doubleQuotedString.parseString(s.strip()).asList()


# TODO: move to fn.py, test/implement
# s = '''
# @fn some_fn
#     hello=$what,
#     foo=${nuts##""},
#     bar=$(crazy),
#     me=5,
#     who="\\"goes\\" there $(echo "what")", third {
# '''
#
# white = pp.White().suppress()
# optionalWhite = pp.Optional(pp.White()).suppress()
# name = pp.Word(pp.alphas + '_', pp.alphanums + '_')
# singleQuotedString = pp.QuotedString("'", unquoteResults=False)
# quotedString = singleQuotedString | doubleQuotedString
# valueComponent = (
#     variable
#     | capturingSubshell
#     | quotedString
#     | pp.Word(pp.printables + '\t ', excludeChars='\'"$`,'))
# value = pp.Combine(pp.OneOrMore(valueComponent))
# defaultValue = pp.Literal('=').suppress() + value
# parameter = pp.Group(name + pp.Optional(defaultValue))
# parameterList = pp.delimitedList(parameter)
#
# fn = (
#     '@fn'
#     + white
#     + name('fn_name')
#     + pp.Optional(white + parameterList)('parameter_list')
#     + optionalWhite
#     + '{'
# )
#
# results = fn.parseString(s).asDict()
#
# pprint(results)
#
# print('name........ ' + results['fn_name'])
#
# if 'parameter_list' in results:
#     for p in results['parameter_list']:
#         print('\nparameter... ' + p[0])
#         if len(p) == 2:
#             print('value....... ' + p[1])
