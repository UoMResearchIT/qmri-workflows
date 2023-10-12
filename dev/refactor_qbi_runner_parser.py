'''
Take a python script.py with Qbi.runner.parser calls of the form:

    parser.add('--param', type=str, default='foo', nargs=?, required=True,
            help='description')
    parser.add('--param2', type=int, default=42, nargs=3, help='description 2')

Write a YAML config file script.config.yaml

    param: 'foo'
    param2: 42

And a JSON-schema file script.schema.yaml

    param:
        type: string
        default: 'foo'
        description: 'description'
        #required: True
    param2:
        type: integer
        default: 42
        description: 'description 2'
        #nargs: 3
'''
import re
import sys

def replace_blocks(input_file, output_file, patterns, block_pattern = r'[\s\S]*'):
        
    with open(input_file, 'r') as file:
        content = file.read()

    if isinstance(block_pattern, str):
        block_pattern = (block_pattern,)

    matches = re.finditer(block_pattern[0], content, re.MULTILINE | re.DOTALL)

    content = ''
    if matches:
        for match in matches:

            matched_text = match.group()

            # Optional block substitution
            if len(block_pattern) == 2:
                matched_text = re.sub(block_pattern[0], block_pattern[1], matched_text)

            # print(f'\n{matched_text}\n')

            # Replace internal patterns
            for old_pattern, new_pattern in patterns:
                matched_text = re.sub(old_pattern, new_pattern, matched_text)

                # print(f'old: {old_pattern}, new: {new_pattern}')
                # print(f'\n{matched_text}\n')

            # Replace the matched text in the original content
            content = content + matched_text + '\n'

        # print(content)

        with open(output_file, 'w') as file:
            file.write(content)

        print(f'Replacements in {input_file} completed successfully.')
    else:
        print('No matches found for the specified block pattern.')

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python refactor_qbi_runner_parser.py <input_file>")
        sys.exit(1)

    input_file_path = sys.argv[1]

    output_schema = re.sub(r'\.py$', r'.schema.yaml', input_file_path)
    output_config = re.sub(r'\.py$', r'.config.yaml', input_file_path)
        
    # Matches complete parser.add(...) call, keeps arguments only
    block_pattern = (r'^\s*parser.add\(([\s\S]*?)\)$', r'\g<1>')

    # Write configuration file with list: param: default
    config_patterns = [
        (r"\n\s+", r' '), # remove line breaks
        (r"^'?--(\w*).*default=(\[[^]]*\]|'[^']*'|[^,)]*).*", r'\g<1>: \g<2>'), # --param, ..., default=foo
        (r"^'?--(\w*).*", r'\g<1>: None')
    ]
    replace_blocks(input_file_path, output_config, config_patterns, block_pattern)

    # Write schema with type, description, etc.
    schema_patterns = [
        (r"\n\s+", r' '), # remove line breaks
        (r"^'?--(\w*)'?", r'\g<1>:'),                                       # --param
        (r",\s*type=([^,)]*)", r'\n  type: \g<1>'),                         # type=foo
        (r",\s*default=(\[[^]]*\]|'[^']*'|[^,)]*)", r'\n  default: \g<1>'),           # default=bar
        (r",\s*help=('[^']*'|[^,)]*)", r'\n  description: \g<1>'),          # help='...'
        (r",\s*nargs='\?'", r''),                                           # dump args='?'
        (r",\s*(\w*)=('[^']*'|[^,)]*)", r'\n  #\g<1>: \g<2>'),              # comment everything else
    ]
    replace_blocks(input_file_path, output_schema, schema_patterns, block_pattern)

    #
    type_patterns = [
        (r"  type: '?str'?", r'  type: string'),
        (r"  type: '?int'?", r'  type: integer'),
        (r"  type: '?float'?", r'  type: number'),
        (r"  type: '?bool_option'?", r'  type: boolean')
    ]
    replace_blocks(output_schema, output_schema, type_patterns)