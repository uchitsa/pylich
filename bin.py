import argparse
import subprocess
import sys
from typing import Callable

from check import check_licenses, filter_failures, get_uncovered_files
from find import find_files


def run():
    parser = argparse.ArgumentParser(description='License header checker', usage='%(prog)s <command> [options]')
    subparsers = parser.add_subparsers(dest='command', help='Command to run')

    check_parser = subparsers.add_parser('check', help='Check license headers')
    check_parser.add_argument('--strict', action='store_true',
                              help='Specifies whether files not covered by the configuration should be treated as errors')
    check_parser.add_argument('--gitignore', action='store_true', help='Ignore git-ignored files')
    check_parser.add_argument('-c', '--config', required=True, help='Path to JSON config file')
    check_parser.add_argument('--path', default='.', help='Path to working directory')

    update_parser = subparsers.add_parser('update', help='Update license headers')
    update_parser.add_argument('-c', '--config', required=True, help='Path to JSON config file')
    update_parser.add_argument('--path', default='.', help='Path to working directory')

    args = parser.parse_args()

    if args.command == 'check':
        check(args.path, args.config, args.strict, args.gitignore)
    else:
        print(f"Unknown command specified, has to be 'check'", file=sys.stderr)
        sys.exit(1)


def check(path: str, config_path: str, strict_mode: bool, gitignore: bool):
    filter_func = create_filter_git_ignored(path) if gitignore else (lambda _: True)
    results = check_licenses(path, config_path, filter_func)
    errors = filter_failures(results)
    missed_files = get_uncovered_files(path, config_path, filter_func)

    for missedFile in missed_files:
        print(f"Config does not cover the file '{missedFile}'", file=sys.stderr)

    for error in errors:
        print(error['message'], file=sys.stderr)

    if strict_mode:
        print(f"{len(errors)} error(s) and {len(missed_files)} warning(s) found. Warnings are treated as errors.",
              file=sys.stderr)
        sys.exit(1 if errors or missed_files else 0)
    elif errors:
        print(f"{len(errors)} error(s) found", file=sys.stderr)
        sys.exit(1)
    else:
        print(f"{len(errors)} error(s) and {len(missed_files)} warning(s) found.")
        sys.exit(0)


def create_filter_git_ignored(path: str) -> Callable[[str], bool]:
    files = find_files(path, ['**'], [])
    ignored_files = set()

    for i in range(0, len(files), 100):
        chunk = files[i:i + 100]
        stdin = '\0'.join(chunk)

        result = subprocess.run(['git', 'check-ignore', '-z', '--stdin'], input=stdin.encode('utf-8'),
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=path)

        for p in result.stdout.decode('utf-8').split('\0'):
            ignored_files.add(p)

    return lambda p: p not in ignored_files


if __name__ == "__main__":
    run()
