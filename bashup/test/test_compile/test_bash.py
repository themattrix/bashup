from ...compile import bash


def test_compile_to_bash():
    fake_compilers = (
        lambda x: 'A(' + x + ')',
        lambda x: 'B(' + x + ')',
        lambda x: 'C(' + x + ')',)

    actual = bash.compile_to_bash('bashup_str', compilers=fake_compilers)

    assert actual == 'C(B(A(bashup_str)))'
