from typing import List, Optional


class LicenseConfig:
    def __init__(self, include: List[str], exclude: Optional[List[str]] = None, license: Optional[str] = None):
        self.include = include
        self.exclude = exclude if exclude is not None else []
        self.license = license


Config = List[LicenseConfig]


def process_config(config: Config):
    for license_config in config:
        print(license_config.include)
        print(license_config.exclude)
        print(license_config.license)

# Example usage:
# config = [
#     LicenseConfig(include=["**/*.js", "**/*.ts"], exclude=["**/node_modules/**", "**/dist/**"], license="MIT"),
#     LicenseConfig(include=["**/*.py"], exclude=["**/env/**"], license="Apache-2.0")
# ]
# process_config(config)
