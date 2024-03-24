from check import check_licenses, filter_failures, get_uncovered_files


def run():
    try:
        path = input('path: ')
        config_path = input('config: ')
        strict_mode = input('strict (true/false): ') == 'true'

        results = check_licenses(path, config_path)
        errors = filter_failures(results)
        missed_files = get_uncovered_files(path, config_path)

        # emit a warning for all missed files:
        for missed_file in missed_files:
            print(f"Config does not cover the file '{missed_file}'")

        # emit an error for all erroneous files:
        for error in errors:
            print(error['message'])

        if strict_mode and (len(errors) != 0 or len(missed_files) != 0):
            print(f"{len(errors)} error(s) and {len(missed_files)} warning(s) found. Warnings are treated as errors.")
        elif len(errors) != 0:
            print(f"{len(errors)} error(s) found")
        else:
            print(f"{len(errors)} error(s) and {len(missed_files)} warning(s) found.")

    except Exception as e:
        print(f"An error occurred: {e}")


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    run()
