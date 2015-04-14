"""Bashup

Usage: bashup --in=BASHUP_FILE [--out=BASH_FILE]
       bashup -h | --help | --version

Options:
  -h --help         Show this help.
  --version         Display the version.
  --in=BASHUP_FILE  The bashup file to compile to bash.
  --out=BASH_FILE   Output compiled bash to this file. Defaults to stdout.

"""
from docopt import docopt
from bashup.compile.bash import compile_to_bash


def compilation(args, compile_fn=compile_to_bash):
    with open(args['--in']) as f:
        in_str = f.read()

    out_str = compile_fn(in_str)

    if args['--out']:
        with open(args['--out'], 'wb') as f:
            f.write(out_str.encode('UTF-8'))
    else:
        print(out_str)  # pylint: disable=superfluous-parens


def main(argv=None):
    compilation(docopt(__doc__, argv, version='Bashup 0.0.1'))


if __name__ == '__main__':
    main()  # pragma: no cover
