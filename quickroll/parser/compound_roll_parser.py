from dice import Dice
from re import (
    findall, fullmatch, match,
)
import parser_regex as PATTERNS

def parse_single_dice_roll(token):
    match = PATTERNS.SINGLE_DICE.match(token)
    times = int(match.group('times') or 1)
    keep = int((match.group('keep') or '0').replace('l', '-'))
    return Dice(times, int(match.group('sides')), keep)


def parse_compound_dice_roll(compound_dice_roll):
    tokens = PATTERNS.COMPOUND_TOKENS_AND_ARGS.findall(compound_dice_roll)
    args = [token[1:] for token in tokens if not PATTERNS.COMPOUND_TOKENS.match(token[0])]
    args = [(x[0], PATTERNS.WHITESPACE.sub('', x[1]).split(',')) for x in args]
    tokens = [token[0] for token in tokens if PATTERNS.COMPOUND_TOKENS.match(token[0])]
    for arg_name, arg_params in args:
        arg_params = [param for param in arg_params if param]
        if len(arg_params) == 0:
            ARGS_TO_FUNC[arg_name](tokens)
        else:
            ARGS_TO_FUNC[arg_name](tokens, *arg_params)
    label = next(iter([token for token in tokens if match(PATTERNS.COMPOUND_TOKENS_DICT['label'], token)]), '')
    tokens = [token for token in tokens if not match(PATTERNS.COMPOUND_TOKENS_DICT['label'], token)]
    tokens_with_dice = list(map(lambda x: parse_single_dice_roll(x) if fullmatch(PATTERNS.SINGLE_DICE, x) else x, tokens))
    tokens_with_dice_result_strings = [str(token) for token in tokens_with_dice]
    tokens_with_dice_result_ints = [str(token.result if type(token) is Dice else token) for token in tokens_with_dice]
    return ' '.join(tokens_with_dice_result_strings) + ' = ' + str(eval(''.join(tokens_with_dice_result_ints))) + ' ' + label[1:-1]


def add(roll_tokens, extra_code):
    if extra_code[0] not in ['-+']:
        roll_tokens.append('+')
    added_tokens = PATTERNS.COMPOUND_TOKENS.findall(extra_code)
    added_tokens = [token for token in added_tokens]
    roll_tokens.extend(added_tokens)


def replace(roll, repl_token, target):
    for index, token in enumerate(roll):
        if fullmatch(f'(?:\d+)?{target}(?:kl?\d*)?', token):
            roll[index] = repl_token


def max_dice(roll):
    for index, token in enumerate(roll):
        if match := PATTERNS.SINGLE_DICE.fullmatch(token):
            times = int(match.group('times') or 1)
            sides = int(match.group('sides'))
            roll[index] = str(times * sides)

ARGS_TO_FUNC = {
    'add': add,
    '+': add,
    'replace': replace,
    'adv': lambda x: replace(x, '2d20k1', 'd20'),
    'dis': lambda x: replace(x, '2d20kl1', 'd20'),
    'max': max_dice,
    'crit': max_dice,
    }