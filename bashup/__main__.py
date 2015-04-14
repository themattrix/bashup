"""Bashup

Usage: bashup (--in=FILE|-i FILE) [--out=FILE|-o FILE]
       bashup -h | --help | --version

Options:
  -h --help           Show this help.
  --version           Display the version.
  -i FILE --in=FILE   The bashup file to compile to bash.
  -o FILE --out=FILE  Output compiled bash to this file. [default: -]

"""
from docopt import docopt
from bashup.compile.bash import compile_to_bash


def compile_file(in_file, out_file, compile_fn=compile_to_bash):
    with open(in_file) as f:
        in_str = f.read()

    out_str = compile_fn(in_str)

    if out_file == '-':
        print(out_str)  # pylint: disable=superfluous-parens
    else:
        with open(out_file, 'wb') as f:
            f.write(out_str.encode('UTF-8'))


def main(argv=None):
    args = docopt(__doc__, argv, version='Bashup 1.0.0')
    compile_file(in_file=args['--in'], out_file=args['--out'])


if __name__ == '__main__':
    main()  # pragma: no cover
