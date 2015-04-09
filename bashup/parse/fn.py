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
# quotedString = singleQuotedString | double_quoted_string
# valueComponent = (
#     variable
#     | capturing_subshell
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
