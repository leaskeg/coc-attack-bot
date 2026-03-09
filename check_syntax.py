import ast
import sys

files = [
    'src/core/auto_attacker.py',
    'src/core/attack_player.py', 
    'src/core/attack_recorder.py'
]

errors = []
for f in files:
    try:
        with open(f) as file:
            ast.parse(file.read())
        print(f'{f}: OK')
    except SyntaxError as e:
        print(f'{f}: ERROR - {e}')
        errors.append(f)

sys.exit(1 if errors else 0)
