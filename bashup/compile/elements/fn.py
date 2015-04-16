from __future__ import division
import jinja2
import re
from textwrap import dedent
from bashup.parse.fn import FN, FnSpec


def compile_fns_to_bash(bashup_str):
    """
    Compiles all @fn statements in the provided bashup string. Returns a new
    string containing the original source but with every @fn statement
    replaced with the equivalent bash code.
    """
    def generate_slices():
        last = 0
        scanner = FN.parseWithTabs().scanString(bashup_str)

        for parse_result, start, end in scanner:
            fn_spec = FnSpec.from_parse_result(parse_result)
            compiled = compile_fn_spec_to_bash(fn_spec)
            initial_indent, body_indent = __guess_indentation(
                before_fn=bashup_str[last:start],
                fn_body=bashup_str[end:])
            yield bashup_str[last:start - len(initial_indent)]
            yield __indent(compiled, initial_indent, body_indent)
            last = end

        yield bashup_str[last:]

    return ''.join(generate_slices())


def compile_fn_spec_to_bash(fn_spec):
    """
    Populates the fn template with the given spec.
    """
    template = jinja2.Environment(
        trim_blocks=True,
        lstrip_blocks=True,
        auto_reload=False,
        autoescape=False,
        newline_sequence='\n'
    ).from_string(__FN_TEMPLATE)

    return template.render(
        fn=fn_spec,
        param_usage=''.join(__usage_for(arg) for arg in fn_spec.args),
        arg_list=' '.join(__quoted_arg(arg) for arg in fn_spec.args))


#
# Private Helpers
#

__FN_TEMPLATE = dedent("""

    #
    # usage: {{ fn.name }} {{ param_usage }}[ARGS]
    #
    {% if fn.args|length %}
    function {{ fn.name }}() {
        {% for arg in fn.args %}
        {% if arg.value is none %}
        local {{ arg.name }}
        local {{ arg.name }}__set=0
        {% else %}
        local {{ arg.name }}={{ arg.value }}
        {% endif %}
        {% endfor %}
        local args=()
        local i

        for ((i = 1; i <= $#; i++)); do
            {% for arg in fn.args %}
            {% set param = "--" ~ arg.name.replace('_', '-') %}
            {% if loop.index == 1 %}
            if [ "${!i}" == "{{ param }}" ]; then
            {% else %}
            elif [ "${!i}" == "{{ param }}" ]; then
            {% endif %}
                ((i++))
                {{ arg.name }}=${!i}
                {% if arg.value is none %}
                {{ arg.name }}__set=1
                {% endif %}
            {% endfor %}
            else
                args+=("${!i}")
            fi
        done

        {% for arg in fn.args %}
        {% if arg.value is none %}
        {% set param = "--" ~ arg.name.replace('_', '-') %}
        if [ {{ "${" ~ arg.name ~ "__set}" }} -eq 0 ]; then
            echo "[ERROR] The {{ param }} parameter must be given."
            return 1
        fi
        {% endif %}
        {% endfor %}

        __{{ fn.name }} {{ arg_list }} "${args[@]}"
    }

    function __{{ fn.name }}() {
        {% for arg in fn.args %}
        local {{ arg.name }}={{ "${" ~ loop.index ~ "}" }}
        {% endfor %}
        shift {{ fn.args|length }}
    {% else %}
    function {{ fn.name }}() {
    {%- endif %}

""").strip()

__DEFAULT_INDENT = ' ' * 4

__BLANK_LINE = re.compile(
    r'^\s*$')

__LEADING_WHITESPACE = re.compile(
    r'^[\t ]*')

__INITIAL_INDENT = re.compile(
    r'(^|\n)(?P<initial_indent>[ \t]*)$')

__BODY_INDENT = re.compile(
    r'^[^\n}]*'                    # don't match a one-line fn
    r'(?:#[^\n]*)?'                # skip comment on the @fn line
    r'(?:[\n\t ]+)*'               # optional blank lines
    r'\n(?P<body_indent>[ \t]*)')  # first non-blank line


def __usage_for(arg):
    param = arg.name.replace('_', '-')
    is_optional = arg.value is not None

    return '{b}--{param} <{PARAM}>{e} '.format(
        param=param,
        PARAM=param.upper(),
        b='[' if is_optional else '',
        e=']' if is_optional else '')


def __quoted_arg(arg):
    return '"${' + arg.name + '}"'


def __strip_prefix(target_str, prefix_str):
    if prefix_str and target_str.startswith(prefix_str):
        return target_str[len(prefix_str):]
    else:
        return target_str


def __indent(target_str, initial, body):
    def __retab_line(line):
        if __BLANK_LINE.match(line):
            return line

        leading_whitespace = len(__LEADING_WHITESPACE.match(line).group())
        depth = leading_whitespace // len(__DEFAULT_INDENT)
        return initial + (body * depth) + line[leading_whitespace:]

    return ''.join(__retab_line(s) for s in target_str.splitlines(True))


def __guess_indentation(before_fn, fn_body):
    match_result = __BODY_INDENT.match(fn_body)
    initial_indent = (
        __INITIAL_INDENT
        .search(before_fn)
        .group('initial_indent'))
    body_indent = (
        __strip_prefix(
            match_result.group('body_indent'),
            initial_indent) if match_result else
        __DEFAULT_INDENT)
    return initial_indent, body_indent
