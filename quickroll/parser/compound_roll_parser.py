from single_roll import Roll
from re import (
    findall, fullmatch, match,
)
import parser_regex as PATTERNS

class RollEquation:
    def __init__(self, tokens, args, is_crit):
        self.tokens = tokens
        self.args = args
        self.is_crit = is_crit


def parse_roll(token, is_max=False, crit=False):
    match = PATTERNS.SINGLE_ROLL.match(token)
    times = int(match.group('times') or 1)
    keep = int((match.group('keep') or '0').replace('l', ''))
    is_higher = 'l' not in (match.group('keep') or '')
    sides = int(match.group('sides'))
    return Roll(times, sides, keep, is_higher, is_max, crit)


def parse_roll_equation(compound_dice_roll, is_crit):
    tokens = PATTERNS.ROLL_COMMAND.findall(compound_dice_roll)
    args = [token[1:] for token in tokens if PATTERNS.ARG.match(token[0])]
    args = [(arg[0], PATTERNS.WHITESPACE.sub('', arg[1]).split(',')) for arg in args]
    label = next(iter([token[3] for token in tokens if PATTERNS.ROLL_EQUATION_LABEL.match(token[0])]), '')
    tokens = [token[0] for token in tokens if PATTERNS.ROLL_EQUATION_TOKENS.match(token[0])]
    modifiers = {'critable': False,
                 'tohit': False,
                 'minimum_to_crit': 20,
                 'is_crit': is_crit,
                 'crit_exclamation': '',
                 'max': False,
    }
    apply_roll_equation_args(tokens, args, modifiers)
    dice_should_crit = modifiers['is_crit'] and modifiers['critable'] and not modifiers['tohit']
    tokens_with_dice = [parse_roll(token, is_max=modifiers['max'], crit=dice_should_crit) if fullmatch(PATTERNS.SINGLE_ROLL, token) else token for token in tokens]
    if modifiers['tohit']:
        d20 = next(iter([dice for dice in tokens_with_dice if type(dice) is Roll and dice.sides == 20]), None)
        if d20.result() >= modifiers['minimum_to_crit']:
            ARGS_TO_FUNC['crit'](tokens, modifiers)
    equation_str = ' '.join([str(token) for token in tokens_with_dice])
    equation_result = roll_equation_result(tokens_with_dice)
    return f'{equation_str} = {equation_result} {label} {modifiers["crit_exclamation"]}', modifiers['is_crit']


def apply_roll_equation_args(tokens, args, modifiers):
    for arg_name, arg_params in args:
        arg_params = [param for param in arg_params if param]
        if arg_name in ARGS_TO_FUNC.keys():
            if len(arg_params) == 0:
                ARGS_TO_FUNC[arg_name](tokens, modifiers)
            else:
                ARGS_TO_FUNC[arg_name](tokens, modifiers, *arg_params)


def roll_equation_result(tokens_with_dice):
    tokens_with_dice_result_ints = [str(token.result() if type(token) is Roll else token) for token in tokens_with_dice]
    return str(eval(''.join(tokens_with_dice_result_ints)))


def add(roll, _, extra_code):
    if extra_code[0] not in ['-+']:
        roll.append('+')
    added_tokens = PATTERNS.ROLL_EQUATION_TOKENS.findall(extra_code)
    added_tokens = [token for token in added_tokens]
    roll.extend(added_tokens)


def replace(roll, _, repl_token, target):
    for index, token in enumerate(roll):
        if fullmatch(f'(?:\d+)?{target}(?:kl?\d*)?', token):
            roll[index] = repl_token


ARGS_TO_FUNC = {
    'add': add,
    '+': add,
    'replace': replace,
    'adv': lambda tokens, _: replace(tokens, _, '2d20k1', 'd20'),
    'dis': lambda tokens, _: replace(tokens, _, '2d20kl1', 'd20'),
    'max': lambda tokens, modifiers: modifiers.update({'max': True}),
    'tohit': lambda tokens, modifiers, *params: modifiers.update({'tohit': True, 'minimum_to_crit': next(iter(params), 20)}),
    'critable': lambda tokens, modifiers: modifiers.update({'critable': True}),
    'crit': lambda tokens, modifiers: modifiers.update({'is_crit': True, 'crit_exclamation': 'CRIT!'}),
    }