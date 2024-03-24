import glob
import os


def find_files(cwd: str, include_patterns: list, exclude_patterns: list) -> list:
    if not include_patterns:
        return []

    include_pattern = include_patterns[0] if len(include_patterns) == 1 else "{" + ",".join(include_patterns) + "}"

    # Construct the full path for each pattern
    include_patterns_full = [os.path.join(cwd, pattern) for pattern in include_patterns]
    exclude_patterns_full = [os.path.join(cwd, pattern) for pattern in exclude_patterns]

    # Use glob to find files
    files = glob.glob(include_pattern, root_dir=cwd, recursive=True)

    # Exclude files that match any exclude pattern
    files = [f for f in files if not any(glob.fnmatch.fnmatch(f, ep) for ep in exclude_patterns_full)]

    # Make the paths absolute
    files = [os.path.join(cwd, f) for f in files]

    return files

# Example usage:
# cwd = 'path/to/your/project'
# include_patterns = ['**/*.js', '**/*.ts']
# exclude_patterns = ['**/node_modules/**', '**/dist/**']
# files = find_files(cwd, include_patterns, exclude_patterns)
# print(files)
