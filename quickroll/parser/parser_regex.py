import re

WHITESPACE = re.compile(r'(\s*)')
SINGLE_ROLL = re.compile(r'(?P<times>\d+)?d(?P<sides>\d+)(?:k(?P<keep>[l-]?\d*))?')
ARG = re.compile(r'(?:(\w+)(?:\((.*?)\))?)')
ROLL_EQUATION_LABEL = re.compile(r'(?:\[([\w\s]*)\])')
ROLL_EQUATION_TOKENS_DICT = {
    'dice_roll': r'(?:(?:\d+)?d\d+(?:kl?\d*)?)',
    'math_operator': r'(?:[+\-*/()])',
    'number': r'(?:\d+)',
}
ROLL_COMMAND = re.compile(f'({"|".join(ROLL_EQUATION_TOKENS_DICT.values())}|{ARG.pattern}|{ROLL_EQUATION_LABEL.pattern})')
ROLL_EQUATION_TOKENS = re.compile(f'({"|".join(ROLL_EQUATION_TOKENS_DICT.values())})')
COMPLETE_ROLL_EQUATION = re.compile(f'({"|".join(ROLL_EQUATION_TOKENS_DICT.values())}|(?:\s))+')

ALIAS_ROLL = re.compile(r'(?:{(.*?)})')
ALIAS_COMMAND = re.compile(f'({ALIAS_ROLL.pattern}|{ARG.pattern})')