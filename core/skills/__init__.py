"""Skills module for XCoder.

This module provides a simple skills system that integrates with the existing
tool management architecture.
"""

import os
import yaml
from pathlib import Path
from typing import List, Dict, Any


def _parse_skill_file(file_path: Path) -> Dict[str, Any]:
    """Parse a skill markdown file with YAML frontmatter.

    Expected format:
    name: Skill Name
    description: Brief description of the skill
    content: |
      # Full skill content

      Detailed instructions and guidelines...

    Args:
        file_path: Path to the skill markdown file

    Returns:
        Dictionary containing name, description, and content
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Parse YAML frontmatter
        if content.startswith('name:'):
            # Simple YAML parsing for our specific format
            lines = content.split('\n')
            skill_data = {}

            i = 0
            while i < len(lines):
                line = lines[i].strip()

                if line.startswith('name:'):
                    skill_data['name'] = line[5:].strip()
                elif line.startswith('description:'):
                    skill_data['description'] = line[12:].strip()
                elif line.startswith('content:'):
                    # Handle multiline content
                    if '|' in line:
                        # Multi-line string
                        content_lines = []
                        i += 1
                        while i < len(lines):
                            content_line = lines[i]
                            if content_line.startswith('  '):  # Indented content
                                content_lines.append(content_line[2:])  # Remove 2-space indent
                            elif content_line.strip() == '':
                                content_lines.append('')
                            else:
                                break
                            i += 1
                        skill_data['content'] = '\n'.join(content_lines).rstrip()
                        i -= 1  # Adjust for the outer loop increment
                    else:
                        skill_data['content'] = line[8:].strip()

                i += 1

            return skill_data
        else:
            # Fallback: treat entire file as content
            skill_name = file_path.stem.replace('_', ' ').title()
            return {
                'name': skill_name,
                'description': f"Skill loaded from {file_path.name}",
                'content': content
            }

    except Exception as e:
        print(f"Error parsing skill file {file_path}: {e}")
        return None


def _load_skills_from_directory() -> List[Dict[str, Any]]:
    """Load all skills from markdown files in the skills directory.

    Returns:
        List of skill dictionaries
    """
    skills = []
    skills_dir = Path(__file__).parent

    # Find all .md files in skills directory and subdirectories
    for md_file in skills_dir.rglob('*.md'):
        # Skip README files
        if md_file.name.lower() in ['readme.md', 'readme.markdown']:
            continue

        skill_data = _parse_skill_file(md_file)
        if skill_data:
            skills.append(skill_data)

    return skills


# Load skills from markdown files
SKILLS = _load_skills_from_directory()
