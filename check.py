import json
import os
import re
from glob import glob
from typing import List, Any, Optional, Callable

CURRENT_YEAR = '%year%'


class Config:
    def __init__(self, config_path: str):
        with open(config_path, 'r') as file:
            self.config = json.load(file)

    def __iter__(self):
        return iter(self.config)


class LicenseConfig:
    def __init__(self, include: List[str], exclude: Optional[List[str]], license: Optional[str]):
        self.include = include
        self.exclude = exclude or []
        self.license = license


class CheckResult:
    def __init__(self, file: str, success: bool, message: Optional[str] = None):
        self.file = file
        self.success = success
        self.message = message


class CheckSuccess(CheckResult):
    def __init__(self, file: str):
        super().__init__(file, True)


class CheckFailure(CheckResult):
    def __init__(self, file: str, message: str):
        super().__init__(file, False, message)


def find_files(cwd: str, include_patterns: List[str], exclude_patterns: List[str]) -> List[str]:
    files = []
    for pattern in include_patterns:
        files.extend(glob(os.path.join(cwd, pattern), recursive=True))
    for pattern in exclude_patterns:
        files = [f for f in files if not re.search(pattern, f)]
    return files


def parse_config(config_string: str) -> Config:
    config_data = json.loads(config_string)
    return Config(config_data)


def check_licenses(cwd: str, config_path: str, filter_path: Optional[Callable[[str], bool]] = None) -> List[
    CheckResult]:
    config = get_config(config_path)
    return check_licenses_with_config(cwd, config, filter_path)


def get_config(config_path: str) -> Config:
    with open(config_path, 'r') as file:
        config_string = file.read()
    return parse_config(config_string)


def check_licenses_with_config(cwd: str, config: Config, path_filter: Optional[Callable[[str], bool]] = None) -> List[
    CheckResult]:
    results = [check_license(cwd, c, path_filter) for c in config]
    return flatten(results)


def get_uncovered_files(cwd: str, config_path: str, path_filter: Optional[Callable[[str], bool]] = None) -> List[str]:
    config = get_config(config_path)
    return get_uncovered_files_with_config(cwd, config, path_filter)


def get_uncovered_files_with_config(cwd: str, config: Config, path_filter: Optional[Callable[[str], bool]] = None) -> \
        List[str]:
    all_files = set(find_files(cwd, ['**'], []))
    if path_filter:
        all_files = {f for f in all_files if path_filter(f)}
    covered_files_results = [get_files(cwd, c) for c in config]
    covered_files = set(flatten(covered_files_results))
    remaining_files = all_files - covered_files
    return list(remaining_files)


def filter_failures(results: List[CheckResult]) -> list[CheckResult]:
    return [f for f in results if not f.success]


def flatten(lst: List[List[Any]]) -> List[Any]:
    return [item for sublist in lst for item in sublist]


def check_license(cwd: str, license_config: LicenseConfig, path_filter: Optional[Callable[[str], bool]] = None) -> List[
    CheckResult]:
    if not license_config.license:
        return []
    license_path = license_config.license if os.path.isabs(license_config.license) else os.path.join(cwd,
                                                                                                     license_config.license)
    error_message_generator = lambda file: f"'{file}' does not contain license from '{license_path}'"
    with open(license_path, 'r') as file:
        license_string = file.read()
    license_regex = convert_header_to_regex(license_string)
    files = get_files(cwd, license_config)
    if path_filter:
        files = [f for f in files if path_filter(f)]
    return [contains(f, license_regex, error_message_generator) for f in files]


def get_files(cwd: str, license_config: LicenseConfig) -> List[str]:
    exclude_patterns = license_config.exclude or []
    return find_files(cwd, license_config.include, exclude_patterns)


def convert_header_to_regex(header: str) -> re.Pattern:
    modified_header = re.escape(header)
    modified_header = modified_header.replace(CURRENT_YEAR, r'\d{4}')
    return re.compile(modified_header)


def contains(file: str, regex: re.Pattern, error_message_generator: Callable[[str], str]) -> CheckResult:
    try:
        with open(file, 'r') as f:
            data = f.read()
        if regex.search(data):
            return CheckSuccess(file)
        else:
            return CheckFailure(file, error_message_generator(file))
    except Exception as e:
        raise Exception(f"Error while reading file '{file}': '{str(e)}'")

# Example usage:
# cwd = 'path/to/your/project'
# config_path = 'path/to/your/config.json'
# results = check_licenses(cwd, config_path)
# failures = filter_failures(results)
# for failure in failures:
#     print(failure.message)
