import string

import itertools
import pyparsing as pp
import pytest

from .. import parse
from .. import test


#
# "@fn" tests
#

@pytest.mark.parametrize('to_parse,expected_result', (
    ('@fn hello {',
     parse.FnSpec(
         name='hello',
         args=())),
    ('@fn\n\r\t hello\n\r\t {',
     parse.FnSpec(
         name='hello',
         args=())),
    ('@fn hello arg {',
     parse.FnSpec(
         name='hello',
         args=(parse.FnArgSpec(name='arg', value=None),))),
    ('@fn hello arg=value {',
     parse.FnSpec(
         name='hello',
         args=(parse.FnArgSpec(name='arg', value='value'),))),
    ('@fn hello arg=9000 {',
     parse.FnSpec(
         name='hello',
         args=(parse.FnArgSpec(name='arg', value='9000'),))),
    ('@fn hello arg=9000over {',
     parse.FnSpec(
         name='hello',
         args=(parse.FnArgSpec(name='arg', value='9000over'),))),
    ('@fn hello arg1=value1, arg2=value2 {',
     parse.FnSpec(
         name='hello',
         args=(parse.FnArgSpec(name='arg1', value='value1'),
               parse.FnArgSpec(name='arg2', value='value2')))),
    ('@fn h a1=v1, a2, a3=v3, a4 {',
     parse.FnSpec(
         name='h',
         args=(parse.FnArgSpec(name='a1', value='v1'),
               parse.FnArgSpec(name='a2', value=None),
               parse.FnArgSpec(name='a3', value='v3'),
               parse.FnArgSpec(name='a4', value=None)))),
    ('@fn h a1=v1,a2,a3=v3,a4{',
     parse.FnSpec(
         name='h',
         args=(parse.FnArgSpec(name='a1', value='v1'),
               parse.FnArgSpec(name='a2', value=None),
               parse.FnArgSpec(name='a3', value='v3'),
               parse.FnArgSpec(name='a4', value=None)))),
    ('''@fn h a1='v1a, v1b', a2, a3="${v3a}, ${v3b}" {''',
     parse.FnSpec(
         name='h',
         args=(parse.FnArgSpec(name='a1', value="'v1a, v1b'"),
               parse.FnArgSpec(name='a2', value=None),
               parse.FnArgSpec(name='a3', value='"${v3a}, ${v3b}"')))),
    ('''@fn h a="", b='' {''',
     parse.FnSpec(
         name='h',
         args=(parse.FnArgSpec(name='a', value='""'),
               parse.FnArgSpec(name='b', value="''")))),
    ('''@fn h a='"', b='"' {''',
     parse.FnSpec(
         name='h',
         args=(parse.FnArgSpec(name='a', value="'\"'"),
               parse.FnArgSpec(name='b', value="'\"'")))),
    ('''@fn h a="'", b="'" {''',
     parse.FnSpec(
         name='h',
         args=(parse.FnArgSpec(name='a', value='"\'"'),
               parse.FnArgSpec(name='b', value='"\'"')))),
    ('''@fn h a="${PATH//"/bin"/"/bun"}", b="\\"" {''',
     parse.FnSpec(
         name='h',
         args=(parse.FnArgSpec(name='a', value='"${PATH//"/bin"/"/bun"}"'),
               parse.FnArgSpec(name='b', value='"\\""')))),
    ('''@fn h a=""''$~$*$_0${}$()``0aA~a@%^*)}/.:?+=-_\\\\$ {''',
     parse.FnSpec(
         name='h',
         args=(parse.FnArgSpec(name='a', value='""\'\'$~$*$_0${}$()``0aA~a@%^*)}/.:?+=-_\\\\$'),))),
))
def test_fn_success_scenarios(to_parse, expected_result):
    parse_result = parse.FN.parseWithTabs().parseString(to_parse)
    actual_result = parse.FnSpec.from_parse_result(parse_result)

    try:
        assert actual_result == expected_result
    except AssertionError:  # pragma: no cover
        raise AssertionError(
            parse_result.asXML() + '\n\n' + test.diff(actual_result, expected_result))  # pragma: no cover


@pytest.mark.parametrize('scenario', (
    '@fn {',
    '@fn arg=value {',
    '@fn name arg={',
    '@fn name arg= {',
    '@fn name arg={} {',
))
def test_fn_failure_scenarios(scenario):
    with pytest.raises(pp.ParseException):
        result = parse.FN.parseWithTabs().parseString(scenario)
        # pylint: disable=superfluous-parens
        print(result.asXML())  # pragma: no cover


#
# name tests
#

VALID_FIRST = (
    string.ascii_letters +
    '_')

VALID_SECOND = (
    string.ascii_letters +
    string.digits +
    '_')

INVALID_FIRST = (
    string.digits +
    string.whitespace +
    string.punctuation.replace('_', ''))

INVALID_SECOND = (
    string.whitespace +
    string.punctuation.replace('_', ''))


# noinspection PyUnresolvedReferences
@pytest.mark.parametrize('scenario', itertools.chain(VALID_FIRST, ('_' + c for c in VALID_SECOND)))
def test_name_identity_scenarios(scenario):
    assert __parse_name(scenario) == scenario


# noinspection PyUnresolvedReferences
@pytest.mark.parametrize('scenario', itertools.chain(INVALID_FIRST, ('_' + c for c in INVALID_SECOND)))
def test_name_failure_scenarios(scenario):
    with pytest.raises(pp.ParseException):
        __parse_name(scenario)


#
# quoted_string tests
#

RAW_ALLOWED_IN_SINGLE_QUOTES = (
    string.printable
    .replace("'", ''))

RAW_ALLOWED_IN_DOUBLE_QUOTES = (
    string.printable
    .replace('"', '')
    .replace('\\', '')
    .replace('`', '')
    .replace('$(', '')
    .replace('${', '')
    .replace('\f', '')
    .replace('\x0b', ''))


def test_quoted_string_validation():
    # Quoted string contains almost all other parsers, so this should validate
    # nested parsers as well.
    parse.QUOTED_STRING.validate()


@pytest.mark.parametrize('scenario', (
    "''",
    "'  '",
    "'${'",
    "'$('",
    "'\"'",
    "'{p}'".format(p=RAW_ALLOWED_IN_SINGLE_QUOTES),
))
def test_single_quoted_string_identity_scenarios(scenario):
    assert __parse_single_quoted_string(scenario) == scenario


@pytest.mark.parametrize('to_parse,expected_result', (
    ("'\\''", "'\\'"),
    ("'${'}", "'${'"),
    ("'$(')", "'$('"),
    ("'\"'\"", "'\"'"),
    ("'{p}'{p}".format(p=RAW_ALLOWED_IN_SINGLE_QUOTES),
     "'{p}'".format(p=RAW_ALLOWED_IN_SINGLE_QUOTES)),
))
def test_single_quoted_string_trimmed_scenarios(to_parse, expected_result):
    assert __parse_single_quoted_string(to_parse) == expected_result


@pytest.mark.parametrize('scenario', (
    '""',
    '"  "',
    '" $) "',
    '" value "',
    '" $ "',
    '" $( "',
    '" ${ "',
    '" ` "',
    '" \\" "',
    '" \\\\\\" "',
    '"{p}"'.format(p=RAW_ALLOWED_IN_DOUBLE_QUOTES),
    '" $var "',
    '" ${} "',
    '" ${_} "',
    '" ${_%%"nested"} "',
    '''" ${_%%'$('} "''',
    '" $() "',
    '" $(echo) "',
    '" $(echo "nested") "',
    '" $(echo "$(echo "nested")") "',
    '''" $(echo '$(') "''',
    '''" $('"') "''',
    '" `` "',
    '" `echo "nested"` "',
    '''" `echo '$('` "''',
    '''" $( ) ${ } ` ` "''',
    '''"$(${`'`'`})${$(`'$('`)}`$(${'${'})`"''',
    '''" $( ${ ` ` } ) ${ $( ` ` ) } ` $( ${ } ) ` "''',
    '''" $( ${ ` '`' ` } ) ${ $( ` '$(' ` ) } ` $( ${ '${' } ) ` "''',
    '''"$(')"''',
    '"\n\r\t "',
    '"$(\n\r\t )"',
    '"${\n\r\t }"',
    '"`\n\r\t `"',
))
def test_double_quoted_string_identity_scenarios(scenario):
    assert __parse_double_quoted_string(scenario) == scenario


@pytest.mark.parametrize('to_parse,expected_result', (
    ('"${"}', '"${"'),
    ('"$(")', '"$("'),
    ('"`"`', '"`"'),
    ('"\'"\'', '"\'"'),
    ('"{p}"{p}'.format(p=RAW_ALLOWED_IN_DOUBLE_QUOTES),
     '"{p}"'.format(p=RAW_ALLOWED_IN_DOUBLE_QUOTES)),
))
def test_double_quoted_string_trimmed_scenarios(to_parse, expected_result):
    assert __parse_double_quoted_string(to_parse) == expected_result


@pytest.mark.parametrize('scenario', (
    '"',
    '"${""}',
    '"$("")',
    '"`""`',
    '"\\"',
    '"$(\'""\')',
))
def test_double_quoted_string_failure_scenarios(scenario):
    with pytest.raises(pp.ParseException):
        __parse_double_quoted_string(scenario)


def test_double_quoted_string_components():
    """
    Validate the internal structure of the string.

    This test is in contrast to the rest which only care about the string as an
    opaque object. It's useful to validate that the string was parsed as
    expected so that the parsing doesn't break in unexpected ways later.
    """
    backticks = "```)``}``'`'`"

    obnoxious = (
        """ $ """
        """ "\\$_" """
        """ '$_' """
        """$~$%$^$&"""
        """$#$*$@$-$!$?$$$_"""
        """$_0,!@#^&*({[-+=\\\\"""
        """'}'"}"$(})"""
        """')'")"${)}"""
        """$()${}$(``)${``}"""
        """'`'"`" """)

    expected_backticks_list = [
        ['`', [], '`'],
        ['`', [')'], '`'],
        ['`', ['}'], '`'],
        ['`', ["'`'"], '`']]

    expected_obnoxious_list = [
        '$',
        ['"', ['\\$', '_'], '"'],
        "'$_'",
        '$', '~',
        '$', '%',
        '$', '^',
        '$', '&',
        ['$', '#'],
        ['$', '*'],
        ['$', '@'],
        ['$', '-'],
        ['$', '!'],
        ['$', '?'],
        ['$', '$'],
        ['$', '_'],
        ['$', '_0'],
        ',!@#^&*({[-+=\\\\',
        "'}'",
        ['"', ['}'], '"'],
        ['$(', ['}'], ')'],
        "')'",
        ['"', [')'], '"'],
        ['${', [')'], '}'],
        ['$(', [], ')'],
        ['${', [], '}'],
        ['$(', [['`', [], '`']], ')'],
        ['${', [['`', [], '`']], '}'],
        "'`'",
        ['"', ['`'], '"']]

    expected_nested_body_list = (
        expected_obnoxious_list +
        expected_backticks_list)

    expected_results_list = [
        ['"',
         [['${', [], '}'],
          ['$(', [], ')'],
          ['`', [], '`'],
          ['${', expected_nested_body_list, '}'],
          ['$(', expected_nested_body_list, ')'],
          ['`', expected_obnoxious_list, '`']],
         '"']]

    to_parse = (
        '"'
        '${{}}$()``'
        '\n\r\t ${{{o}{b}}}'
        '\n\r\t $({o}{b})'
        '\n\r\t `{o}`'
        '"'
    ).format(
        o=obnoxious,
        b=backticks)

    # pylint: disable=superfluous-parens
    print(repr(to_parse))

    parse_result = (
        parse
        .DOUBLE_QUOTED_STRING_UNCOMBINED
        .parseWithTabs()
        .parseString(to_parse))

    results_list = parse_result.asList()

    try:
        assert results_list == expected_results_list
    except AssertionError:  # pragma: no cover
        raise AssertionError(
            parse_result.asXML() + '\n\n' + test.diff(results_list, expected_results_list))  # pragma: no cover


#
# value tests
#

INVALID_VALUE_CHARS = '"\'`\n\r\t ;,{([#!&<>|'


@pytest.mark.parametrize('scenario', (
    '3',
    '$',
    ')',
    '))',
    '$))3',
    '}',
    '}}',
    '$}}3',
    '\\',
    '\\\\',
    '""\'\'$~$*$_0${}$()``0aA~a@%^*)}/.:?+=-_\\\\$',))
def test_value_identity_scenarios(scenario):
    assert __parse_value(scenario) == scenario


# noinspection PyUnresolvedReferences
@pytest.mark.parametrize('to_parse,expected_result', itertools.chain(
    ((''.join(('1', c, '2')), '1') for c in INVALID_VALUE_CHARS),
    (('";";1', '";"'),
     ("';';1", "';'"),
     ("`;`;1", "`;`"),
     ("$(;);1", "$(;)"),
     ("${;};1", "${;}")),
))
def test_value_trimmed_scenarios(to_parse, expected_result):
    assert __parse_value(to_parse) == expected_result


@pytest.mark.parametrize('scenario', itertools.chain(('',), INVALID_VALUE_CHARS))
def test_value_failure_scenarios(scenario):
    with pytest.raises(pp.ParseException):
        __parse_value(scenario)


#
# variable tests
#

@pytest.mark.parametrize('scenario', (
    '$_',
    '${_}',
    '${"}"}',
    "${'}'}",
    '${"${"${nested}"}"}',
    "${'${'${nested}'}'}",
))
def test_variable_identity_scenarios(scenario):
    assert __parse_variable(scenario) == scenario


@pytest.mark.parametrize('scenario', (
    '$',
    '${',
    '${"}"',
    "${'}'",
))
def test_variable_failure_scenarios(scenario):
    with pytest.raises(pp.ParseException):
        __parse_variable(scenario)


#
# Test Helpers
#

def __parse_name(to_parse):
    return (
        (pp.StringStart() + parse.NAME('result') + pp.StringEnd())
        .leaveWhitespace()
        .parseWithTabs()
        .parseString(to_parse))['result']


def __parse_single_quoted_string(to_parse):
    return (
        parse.SINGLE_QUOTED_STRING('result')
        .parseWithTabs()
        .parseString(to_parse))['result']


def __parse_double_quoted_string(to_parse):
    print(
        parse.DOUBLE_QUOTED_STRING_UNCOMBINED
        .parseWithTabs()
        .parseString(to_parse)
        .asXML())

    return (
        parse.DOUBLE_QUOTED_STRING('result')
        .parseWithTabs()
        .parseString(to_parse))['result']


def __parse_value(to_parse):
    return (
        pp.originalTextFor(parse.VALUE)('result')
        .leaveWhitespace()
        .parseWithTabs()
        .parseString(to_parse))['result']


def __parse_variable(to_parse):
    return (
        pp.originalTextFor(parse.VARIABLE)('result')
        .leaveWhitespace()
        .parseWithTabs()
        .parseString(to_parse))['result']
