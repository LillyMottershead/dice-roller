from dice import Dice
from re import (
    findall, fullmatch, match,
)
import parser_regex as PATTERNS

def parse_single_dice_roll(token, max=False, crit=False):
    match = PATTERNS.SINGLE_DICE.match(token)
    times = int(match.group('times') or 1)
    keep = int((match.group('keep') or '0').replace('l', '-'))
    return Dice(times, int(match.group('sides')), keep, max, crit)


def parse_compound_dice_roll(compound_dice_roll, is_crit):
    tokens = PATTERNS.COMPOUND_TOKENS_AND_ARGS.findall(compound_dice_roll)
    args = [token[1:] for token in tokens if not PATTERNS.COMPOUND_TOKENS.match(token[0])]
    args = [(x[0], PATTERNS.WHITESPACE.sub('', x[1]).split(',')) for x in args]
    tokens = [token[0] for token in tokens if PATTERNS.COMPOUND_TOKENS.match(token[0])]
    modifiers = {'critable': False,
                 'tohit': False,
                 'minimum_to_crit': 20,
                 'max': False,
    }
    for arg_name, arg_params in args:
        arg_params = [param for param in arg_params if param]
        if arg_name in ARGS_TO_FUNC.keys():
            if len(arg_params) == 0:
                ARGS_TO_FUNC[arg_name](tokens, modifiers)
            else:
                ARGS_TO_FUNC[arg_name](tokens, modifiers, *arg_params)
    label = next(iter([token for token in tokens if match(PATTERNS.COMPOUND_TOKENS_DICT['label'], token)]), '')
    tokens = [token for token in tokens if not match(PATTERNS.COMPOUND_TOKENS_DICT['label'], token)]
    tokens_with_dice = list(map(lambda x: parse_single_dice_roll(x, max=modifiers['max'], crit=is_crit) if fullmatch(PATTERNS.SINGLE_DICE, x) else x, tokens))
    if modifiers['tohit']:
        d20 = next(iter([dice for dice in tokens_with_dice if type(dice) is Dice and dice.sides == 20]), None)
        is_crit = d20.result >= modifiers['minimum_to_crit']
    tokens_with_dice_result_strings = [str(token) for token in tokens_with_dice]
    tokens_with_dice_result_ints = [str(token.result if type(token) is Dice else token) for token in tokens_with_dice]
    crit_exclamation = 'CRIT!' if is_crit else ''
    return ' '.join(tokens_with_dice_result_strings) + ' = ' + str(eval(''.join(tokens_with_dice_result_ints))) + ' ' + label[1:-1] + crit_exclamation, is_crit


def add(roll, _, extra_code):
    if extra_code[0] not in ['-+']:
        roll.append('+')
    added_tokens = PATTERNS.COMPOUND_TOKENS.findall(extra_code)
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
    'adv': lambda x, y, z: replace(x, z, '2d20k1', 'd20'),
    'dis': lambda x, y, z: replace(x, z, '2d20kl1', 'd20'),
    'max': lambda x, y: y.update({'max': True}),
    'tohit': lambda x, y, *z: y.update({'tohit': True, 'minimum_to_crit': next(iter(z), 20)}),
    'critable': lambda x, y: y.update({'critable': True}),
    }