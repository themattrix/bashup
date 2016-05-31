from .elements import fn


ALL_COMPILERS = (
    fn.compile_fns_to_bash,)


def compile_to_bash(bashup_str, compilers=ALL_COMPILERS):
    """
    Compiles the given bashup code to bash, returning a string.
    """
    for c in compilers:
        bashup_str = c(bashup_str)

    return bashup_str
