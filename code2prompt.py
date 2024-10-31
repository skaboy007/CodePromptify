import os
import argparse
import glob
import json
import subprocess
import sys
import re
from pathlib import Path

try:
    import tiktoken  # For token counting
except ImportError:
    print("tiktoken module not found. Please install it using 'pip install tiktoken'")
    sys.exit(1)

try:
    import pyperclip  # For copying to clipboard
except ImportError:
    pyperclip = None  # Clipboard functionality will be disabled

try:
    import jinja2  # For templating
except ImportError:
    print("jinja2 module not found. Please install it using 'pip install Jinja2'")
    sys.exit(1)

from gitignore_parser import parse_gitignore  # To respect .gitignore

def get_file_contents(file_path, line_numbers=False):
    """Reads the content of a file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            if line_numbers:
                lines = file.readlines()
                content = ''.join(f"{idx+1}: {line}" for idx, line in enumerate(lines))
            else:
                content = file.read()
            return content
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return ""

def gather_project_files_content(directory, include_patterns=None, exclude_patterns=None, exclude_from_tree=False, line_numbers=False, codeblock=True, gitignore=None):
    """Gathers the contents of all files in the directory and its subdirectories, applying include and exclude patterns."""
    all_files = []
    directory = Path(directory)

    # Compile include and exclude patterns
    includes = [pattern.strip() for pattern in include_patterns.split(',')] if include_patterns else []
    excludes = [pattern.strip() for pattern in exclude_patterns.split(',')] if exclude_patterns else []

    for root, dirs, files in os.walk(directory):
        root = Path(root)

        # Exclude directories based on gitignore and exclude patterns
        dirs[:] = [d for d in dirs if not (gitignore and gitignore(os.path.join(root, d)))]

        for d in list(dirs):
            dir_path = root / d
            if any(dir_path.match(pattern) for pattern in excludes):
                dirs.remove(d)

        for file_name in files:
            file_path = root / file_name

            # Exclude files based on gitignore and exclude patterns
            if gitignore and gitignore(str(file_path)):
                continue

            if any(file_path.match(pattern) for pattern in excludes):
                continue

            if includes and not any(file_path.match(pattern) for pattern in includes):
                continue

            relative_path = file_path.relative_to(directory)
            content = get_file_contents(file_path, line_numbers=line_numbers)
            if content:
                if codeblock:
                    formatted_content = f"### {relative_path}\n```{file_path.suffix[1:]}\n{content}\n```\n"
                else:
                    formatted_content = f"### {relative_path}\n{content}\n"
                all_files.append({
                    'path': str(relative_path),
                    'content': content,
                    'formatted_content': formatted_content
                })

    return all_files

def count_stats(content, model="gpt-3.5-turbo"):
    """Counts the number of lines, words, characters, and tokens in the content."""
    lines = content.count('\n')
    words = len(content.split())
    chars = len(content)

    # Initialize tiktoken encoder for the model
    encoding = tiktoken.encoding_for_model(model)
    tokens = len(encoding.encode(content))

    return lines, words, chars, tokens

def save_to_file(output_path, content):
    """Saves the gathered content to a file."""
    try:
        with open(output_path, 'w', encoding='utf-8') as output_file:
            output_file.write(content)
        print(f"Exported to {output_path}")
    except Exception as e:
        print(f"Error saving to {output_path}: {e}")

def copy_to_clipboard(content):
    """Copies content to the clipboard."""
    if pyperclip:
        pyperclip.copy(content)
        print("Content copied to clipboard.")
    else:
        print("pyperclip module not found. Cannot copy to clipboard.")

def get_git_diff(directory, staged=False, branches=None):
    """Gets the git diff output."""
    diff_output = ""
    os.chdir(directory)
    try:
        if branches:
            branches = branches.split(',')
            if len(branches) == 2:
                diff_output = subprocess.check_output(['git', 'diff', branches[0].strip(), branches[1].strip()], universal_newlines=True)
            else:
                print("Please provide exactly two branch names separated by a comma.")
        elif staged:
            diff_output = subprocess.check_output(['git', 'diff', '--staged'], universal_newlines=True)
        else:
            diff_output = subprocess.check_output(['git', 'diff'], universal_newlines=True)
    except subprocess.CalledProcessError as e:
        print(f"Error getting git diff: {e}")
    return diff_output

def main():
    parser = argparse.ArgumentParser(description='Generate a prompt from a codebase directory.')
    parser.add_argument('directory', help='Path to the codebase directory.')
    parser.add_argument('-t', '--template', help='Path to the Handlebars (Jinja2) template file.')
    parser.add_argument('--include', help='Glob patterns to include, comma-separated.')
    parser.add_argument('--exclude', help='Glob patterns to exclude, comma-separated.')
    parser.add_argument('--exclude-from-tree', action='store_true', help='Exclude files/folders from the source tree based on exclude patterns.')
    parser.add_argument('--tokens', action='store_true', help='Display the token count of the generated prompt.')
    parser.add_argument('--encoding', default='cl100k_base', help='Specify a tokenizer for token count.')
    parser.add_argument('--output', help='Save the generated prompt to an output file.')
    parser.add_argument('--json', action='store_true', help='Print output as JSON.')
    parser.add_argument('--diff', action='store_true', help='Include git diff output (staged files) in the generated prompt.')
    parser.add_argument('--git-diff-branch', help='Compare branches and get diff output, format: branch1,branch2.')
    parser.add_argument('--git-log-branch', help='Get git log between branches, format: branch1,branch2.')
    parser.add_argument('--line-number', action='store_true', help='Add line numbers to source code blocks.')
    parser.add_argument('--no-codeblock', action='store_true', help='Disable wrapping code inside markdown code blocks.')
    parser.add_argument('--copy', action='store_true', help='Copy the generated prompt to the clipboard.')
    args = parser.parse_args()

    directory = args.directory
    template_path = args.template
    include_patterns = args.include
    exclude_patterns = args.exclude
    exclude_from_tree = args.exclude_from_tree
    show_tokens = args.tokens
    encoding_name = args.encoding
    output_path = args.output
    output_json = args.json
    diff = args.diff
    git_diff_branch = args.git_diff_branch
    git_log_branch = args.git_log_branch
    line_numbers = args.line_number
    codeblock = not args.no_codeblock
    copy = args.copy

    # Parse .gitignore
    gitignore_file = os.path.join(directory, '.gitignore')
    gitignore = None
    if os.path.exists(gitignore_file):
        gitignore = parse_gitignore(gitignore_file)

    # Gather all file contents
    files_data = gather_project_files_content(
        directory,
        include_patterns=include_patterns,
        exclude_patterns=exclude_patterns,
        exclude_from_tree=exclude_from_tree,
        line_numbers=line_numbers,
        codeblock=codeblock,
        gitignore=gitignore
    )

    # Get git diff output if needed
    git_diff_output = ""
    if diff or git_diff_branch or git_log_branch:
        git_diff_output = get_git_diff(directory, staged=diff, branches=git_diff_branch)

    # Load template
    if template_path:
        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()
    else:
        # Default template
        template_content = """
# Codebase: {{ directory_name }}

{% for file in files %}
{{ file.formatted_content }}
{% endfor %}

{% if git_diff_output %}
# Git Diff Output

{% endif %}

Total Tokens: {{ token_count }}
"""

    # Prepare context for the template
    all_formatted_content = '\n'.join(file['formatted_content'] for file in files_data)
    full_prompt = all_formatted_content

    # Token count
    encoding = tiktoken.get_encoding(encoding_name)
    token_count = len(encoding.encode(full_prompt))

    context = {
        'directory_name': os.path.basename(directory),
        'files': files_data,
        'git_diff_output': git_diff_output,
        'token_count': token_count
    }

    # Render template
    template = jinja2.Template(template_content)
    output_content = template.render(context)

    # Output
    if output_json:
        output_data = {
            'prompt': output_content,
            'directory_name': context['directory_name'],
            'token_count': context['token_count'],
            'model_info': 'ChatGPT models, text-embedding-ada-002',
            'files': [file['path'] for file in files_data]
        }
        print(json.dumps(output_data, indent=2))
    else:
        print(output_content)

    if output_path:
        save_to_file(output_path, output_content)

    if show_tokens:
        print(f"Total Tokens: {token_count}")

    if copy:
        copy_to_clipboard(output_content)

if __name__ == "__main__":
    main()
