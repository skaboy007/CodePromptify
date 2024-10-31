Effortlessly generate well-formatted Markdown prompts from your codebase to use with large language models (LLMs) like GPT or Claude. This tool traverses your project's source tree, compiles code files according to your specifications, and prepares a prompt ready for LLM consumption.

Table of Contents
Features
Installation
Usage
Basic Prompt Generation
Custom Template
File Filtering
Excluding from Source Tree
Token Count Display
Git Integration
Output Options
Code Formatting Options
Use Cases
Template Customization
Requirements
Contributing
License
Features
Comprehensive Codebase Parsing: Automatically includes all source files, respecting your .gitignore configurations.
Customizable Templates: Utilize Jinja2 templates to customize the output prompt according to your needs.
File Filtering: Include or exclude files using glob patterns for precise control over which files are processed.
Token Count Display: Shows the token count of the generated prompt, helping you stay within LLM context windows.
Git Integration:
Git Diff Output: Optionally include Git diff outputs (staged files or between branches) in your prompt.
Git Log Output: Incorporate Git log messages between branches.
Clipboard Support: Automatically copy the generated prompt to your clipboard for quick pasting.
Output Saving: Save the generated prompt to a file for future reference.
Exclude Specific Files/Folders: Easily exclude files or directories by name or path.
Line Numbering: Add line numbers to your source code blocks for better readability.
Code Block Formatting: Choose whether to wrap code inside markdown code blocks.
Installation
Before using Code2Prompt, ensure you have the necessary Python packages installed:

bash
Copy code
pip install tiktoken pyperclip Jinja2 gitignore_parser
Usage
Basic Prompt Generation
Generate a prompt from a codebase directory:

bash
Copy code
python code2prompt.py /path/to/codebase
Custom Template
Use a custom Jinja2 template to format the prompt:

bash
Copy code
python code2prompt.py /path/to/codebase -t /path/to/template.jinja
File Filtering
Include specific files using glob patterns:

bash
Copy code
python code2prompt.py /path/to/codebase --include="*.py,*.md"
Exclude specific files using glob patterns:

bash
Copy code
python code2prompt.py /path/to/codebase --exclude="*.txt,*.md"
Excluding from Source Tree
Exclude files or folders from the source tree based on patterns:

bash
Copy code
python code2prompt.py /path/to/codebase --exclude="*.npy,*.wav" --exclude-from-tree
Token Count Display
Display the token count of the generated prompt:

bash
Copy code
python code2prompt.py /path/to/codebase --tokens
Specify a tokenizer for token counting (supports cl100k_base, p50k_base, p50k_edit, r50k_base):

bash
Copy code
python code2prompt.py /path/to/codebase --tokens --encoding=p50k_base
Git Integration
Include Git diff output for staged files:

bash
Copy code
python code2prompt.py /path/to/codebase --diff
Compare branches and include Git diff output:

bash
Copy code
python code2prompt.py /path/to/codebase --git-diff-branch="main,development"
Include Git log messages between branches:

bash
Copy code
python code2prompt.py /path/to/codebase --git-log-branch="main,development"
Output Options
Save the generated prompt to a file:

bash
Copy code
python code2prompt.py /path/to/codebase --output=output.txt
Copy the generated prompt to the clipboard:

bash
Copy code
python code2prompt.py /path/to/codebase --copy
Print output as JSON:

bash
Copy code
python code2prompt.py /path/to/codebase --json
The JSON output structure:

json
Copy code
{
  "prompt": "<Generated Prompt>",
  "directory_name": "codebase",
  "token_count": 1234,
  "model_info": "ChatGPT models, text-embedding-ada-002",
  "files": [
    "file1.py",
    "file2.md",
    "... more files"
  ]
}
Code Formatting Options
Add line numbers to source code blocks:

bash
Copy code
python code2prompt.py /path/to/codebase --line-number
Disable wrapping code inside markdown code blocks:

bash
Copy code
python code2prompt.py /path/to/codebase --no-codeblock
Use Cases
LLM Prompt Generation: Quickly prepare your codebase as a prompt for large context window models like GPT-4 or Claude.
Code Translation: Generate prompts to rewrite your code in another programming language.
Bug and Security Analysis: Prepare code for analysis by LLMs to find bugs or security vulnerabilities.
Documentation Generation: Use the tool to create prompts that help in documenting your codebase.
Feature Implementation: Generate prompts to assist in brainstorming or implementing new features with the help of LLMs.
Template Customization
The tool uses Jinja2 for templating, allowing you to create custom templates that suit your needs. Here's an example of a simple template:

jinja
Copy code
# Project: {{ directory_name }}

{% for file in files %}
## {{ file.path }}

```{{ file.path.split('.')[-1] }}
{{ file.content }}
{% endfor %}

{% if git_diff_output %}

Git Diff Output
Copy code
{{ git_diff_output }}
{% endif %}

Total Tokens: {{ token_count }}

markdown
Copy code

You can specify your template file using the `-t` or `--template` option.

## Requirements

- **Python 3.6 or higher**
- **Dependencies**: Install via pip:

  ```bash
  pip install tiktoken pyperclip Jinja2 gitignore_parser
Git: Required for Git integration features.
Contributing
Contributions are welcome! Feel free to submit issues or pull requests on GitHub.

License
This project is licensed under the MIT License.