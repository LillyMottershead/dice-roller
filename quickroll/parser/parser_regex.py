import re

WHITESPACE = re.compile(r'(\s*)')
SINGLE_DICE = re.compile(r'(?P<times>\d+)?d(?P<sides>\d+)(?:k(?P<keep>[l-]?\d*))?')
COMPOUND_ARG = re.compile(r'(?:(\w+)(?:\((.*?)\))?)')
COMPOUND_TOKENS_DICT = {
    'dice_roll': r'(?:(?:\d+)?d\d+(?:kl?\d*)?)',
    'math_operator': r'(?:[+\-*/()])',
    'number': r'(?:\d+)',
    'label': r'(?:\[[\w\s]*\])',
}
COMPOUND_TOKENS_AND_ARGS = re.compile(f'({"|".join(COMPOUND_TOKENS_DICT.values())}|{COMPOUND_ARG.pattern})')
COMPOUND_TOKENS = re.compile(f'({"|".join(COMPOUND_TOKENS_DICT.values())})')
COMPLETE_COMPOUND_ROLL = re.compile(f'({"|".join(COMPOUND_TOKENS_DICT.values())}|(?:\s))+')