"""Bashup

Usage: bashup (--in=FILE|-i FILE) [--out=FILE|-o FILE]
       bashup (--run=FILE|-r FILE) [-- <arg>...]
       bashup -h | --help | --version

Options:
  -h --help           Show this help.
  --version           Display the version.
  -i FILE --in=FILE   The bashup file to compile to bash.
  -o FILE --out=FILE  Output compiled bash to this file. [default: -]
  -r FILE --run=FILE  Run the script directly. Args are passed to the script.

"""
import subprocess
import sys

import docopt
import temporary

from .compile import bash


def compile_file(in_file, out_file, compile_fn=bash.compile_to_bash):
    """
    Compile the in_file and write it to the out_file. If out_file is
    '-', then the compiled code is written to stdout instead.
    """
    with open(str(in_file)) as f:
        in_str = f.read()

    out_str = compile_fn(in_str)

    if str(out_file) == '-':
        print(out_str)  # pylint: disable=superfluous-parens
    else:
        with open(str(out_file), 'wb') as f:
            f.write(out_str.encode('utf-8'))


def run_file(to_run, args, compile_fn=bash.compile_to_bash, run_fn=subprocess.call, temp_file_ctx=temporary.temp_file):
    """
    Compile the to_run file, write it to a temporary file, and run it
    with bash. Any additional parameters to bashup are passed along to
    the script.
    """
    with open(str(to_run)) as f:
        run_str = f.read()

    with temp_file_ctx(compile_fn(run_str)) as script:
        return run_fn(('bash', str(script)) + tuple(args))


def main(argv=None, run_fn=run_file, compile_fn=compile_file):
    args = docopt.docopt(__doc__, argv, version='Bashup 2.0.2')

    if args['--in'] is None:
        return run_fn(to_run=args['--run'], args=tuple(args['<arg>']))
    else:
        compile_fn(in_file=args['--in'], out_file=args['--out'])
        return 0


if __name__ == '__main__':
    sys.exit(main())  # pragma: no cover
