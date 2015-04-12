import jinja2
from textwrap import dedent


# def compile_fns_to_bash(bashup_str):
#     """
#     Compiles all @fn statements in the provided bashup string. Returns a new
#     string containing the original source but with every @fn statement
#     replaced with the equivalent bash code.
#     """
#     return bashup_str


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

    # <generated>
    #
    # usage: {{ fn.name }} {{ param_usage }}[ARGS]
    #
    function {{ fn.name }}() {
        {% if fn.args|length %}
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

        for ((i = 1; i < $#; i++)); do
            {% for arg in fn.args %}
            {% set param = "--" ~ arg.name.replace('_', '-') %}
            {% if loop.index == 1 %}
            if [ "{{ "${!i}" }}" == "{{ param }}" ]; then
            {% else %}
            elif [ "{{ "${!i}" }}" == "{{ param }}" ]; then
            {% endif %}
                ((i++))
                {{ arg.name }}={{ "${!i}" }}
                {% if arg.value is none %}
                {{ arg.name }}__set=1
                {% endif %}
            {% endfor %}
            else
                args+=("{{ "${!i}" }}")
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

        __{{ fn.name }} {{ arg_list }} "{{ "${args[@]}" }}"
    }

    function __{{ fn.name }}() {
        {% for arg in fn.args %}
        local {{ arg.name }}={{ "${" ~ loop.index ~ "}" }}
        {% endfor %}
        shift {{ fn.args|length }}

        {% endif %}
        # </generated>

""").strip()

# __DEFAULT_INDENT = ' ' * 4


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
