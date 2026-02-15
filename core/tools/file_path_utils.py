"""
Shared file path utilities for intelligent path resolution
"""

import os
import glob


def resolve_file_path(file_path: str, base_dir: str = None) -> str:
    """Intelligent path resolution supporting relative paths and project search.

    Args:
        file_path: The path to resolve
        base_dir: Base directory to resolve from (defaults to current working directory)

    Returns:
        Resolved absolute path
    """
    if base_dir is None:
        base_dir = os.getcwd()

    # If already absolute, return as-is
    if os.path.isabs(file_path):
        return file_path

    # Try direct relative path from base_dir
    relative_path = os.path.join(base_dir, file_path)
    if os.path.exists(relative_path):
        return os.path.abspath(relative_path)

    # Handle paths starting with ../ - resolve relative to base_dir
    if file_path.startswith('../'):
        try:
            resolved = os.path.abspath(os.path.join(base_dir, file_path))
            if os.path.exists(resolved):
                return resolved
        except Exception:
            pass

    # Try to find file by name in project tree
    file_name = os.path.basename(file_path)
    if file_name:
        # Search in current directory and subdirectories
        for root, dirs, files in os.walk(base_dir):
            if file_name in files:
                candidate = os.path.join(root, file_name)
                # Check if the full relative path matches the end of candidate path
                candidate_relative = os.path.relpath(candidate, base_dir)
                if file_path.endswith(candidate_relative) or candidate_relative.endswith(file_path):
                    return candidate

        # Search in parent directories if not found in subdirectories
        parent_dir = os.path.dirname(base_dir)
        while parent_dir != os.path.dirname(parent_dir):  # Stop at filesystem root
            for root, dirs, files in os.walk(parent_dir):
                if file_name in files:
                    candidate = os.path.join(root, file_name)
                    # Check if this matches our expected path structure
                    try:
                        rel_from_parent = os.path.relpath(candidate, parent_dir)
                        if file_path in rel_from_parent or rel_from_parent.endswith(file_path):
                            return candidate
                    except ValueError:
                        continue
            parent_dir = os.path.dirname(parent_dir)

    # Try glob pattern matching for flexibility
    if '*' in file_path or '?' in file_path:
        matches = glob.glob(os.path.join(base_dir, file_path))
        if matches:
            return os.path.abspath(matches[0])

    # If all else fails, return the original path joined with base_dir
    # This will let the original error handling in file_operations work
    return os.path.join(base_dir, file_path)


def find_project_files(pattern: str, base_dir: str = None) -> list:
    """Find files matching a pattern in the project directory.

    Args:
        pattern: File pattern to search for (supports wildcards)
        base_dir: Base directory to search from

    Returns:
        List of matching file paths
    """
    if base_dir is None:
        base_dir = os.getcwd()

    matches = []

    # Direct glob search
    glob_pattern = os.path.join(base_dir, "**", pattern)
    matches.extend(glob.glob(glob_pattern, recursive=True))

    # Also search in parent directories
    parent_dir = os.path.dirname(base_dir)
    while parent_dir != os.path.dirname(parent_dir):
        parent_glob = os.path.join(parent_dir, "**", pattern)
        parent_matches = glob.glob(parent_glob, recursive=True)
        matches.extend(parent_matches)
        parent_dir = os.path.dirname(parent_dir)

        # Limit search depth to avoid going too far up
        if len(parent_dir.split(os.sep)) < 3:
            break

    return list(set(matches))  # Remove duplicates