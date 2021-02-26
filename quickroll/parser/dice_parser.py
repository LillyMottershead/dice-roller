from dice import Dice
from inspect import signature
import re


blank_space_pattern = re.compile(r'(\s*)')
single_dice_roll_pattern = re.compile(r'(?P<times>\d+)?d(?P<sides>\d+)(?:k(?P<keep>[l-]?\d*))?')
args_pattern = re.compile(r'(?:(\w+)(?:\((.*?)\))?)')
valid_tokens = {
    'dice_roll': r'(?:(?:\d+)?d\d+(?:kl?\d*)?)',
    'math_operator': r'(?:[+\-*/()])',
    'number': r'(?:\d+)',
    'label': r'(?:\[[\w\s]*\])',
    'arg':  args_pattern.pattern,
}
valid_compound_tokens_pattern = re.compile('(' + '|'.join(valid_tokens.values()) + ')')
valid_tokens.pop('arg')
valid_compound_tokens_no_args_pattern = re.compile('(' + '|'.join(valid_tokens.values()) + ')')
complete_compound_dice_roll_pattern = re.compile('(' + '|'.join(valid_tokens.values()) + r'|(?:\s))+')

aliases = set()
alias_to_code = {}

def parse_single_dice_roll(token):
    match = single_dice_roll_pattern.match(token)
    times = int(match.group('times') or 1)
    keep = int((match.group('keep') or '0').replace('l', '-'))
    return Dice(times, int(match.group('sides')), keep)


def parse_compound_dice_roll(compound_dice_roll):
    tokens = valid_compound_tokens_pattern.findall(compound_dice_roll)
    args = [token[1:] for token in tokens if not valid_compound_tokens_no_args_pattern.match(token[0])]
    args = [(x[0], blank_space_pattern.sub('', x[1]).split(',')) for x in args]
    tokens = [token[0] for token in tokens if valid_compound_tokens_no_args_pattern.match(token[0])]
    for arg_name, arg_params in args:
        roll_args_to_func[arg_name](tokens, *arg_params)
    label = next(iter([token for token in tokens if re.match(valid_tokens['label'], token)]), '')
    tokens = [token for token in tokens if not re.match(valid_tokens['label'], token)]
    tokens_with_dice_objects = list(map(lambda x: parse_single_dice_roll(x) if re.fullmatch(single_dice_roll_pattern, x) else x, tokens))
    tokens_with_dice_result_strings = list(map(str, tokens_with_dice_objects))
    tokens_with_dice_result_ints = list(map(lambda x: str(x.result) if type(x) is Dice else x, tokens_with_dice_objects))
    return ' '.join(tokens_with_dice_result_strings) + ' = ' + str(eval(''.join(tokens_with_dice_result_ints))) + ' ' + label[1:-1]


def add(roll_tokens, extra_code):
    if extra_code[0] not in ['-+']:
        roll_tokens.append('+')
    added_tokens = valid_compound_tokens_pattern.findall(extra_code)
    added_tokens = [token[0] for token in added_tokens]
    roll_tokens.extend(added_tokens)


def replace(roll, repl_token, target):
    for index, token in enumerate(roll):
        if re.fullmatch(f'(?:\d+)?{target}(?:kl?\d*)?', token):
            roll[index] = repl_token


def max_dice(*roll):
    roll = roll[0]
    for index, token in enumerate(roll):
        if match := single_dice_roll_pattern.fullmatch(token):
            times = int(match.group('times') or 1)
            sides = int(match.group('sides'))
            roll[index] = str(times * sides)


def parse_command(command, inner=False):
    first_arg = tuple(command.split(' ', 1))[0]
    if first_arg == 'alias':
        return alias_command(command)
    elif first_arg in aliases:
        code = alias_to_code[first_arg].copy()
        try:
            second_arg = tuple(command.split(' ', 1))[1]
            args = args_pattern.findall(second_arg)
            args = list(map(lambda x: (x[0], blank_space_pattern.sub('', x[1]).split(',')), args))
        except IndexError:
            args = []
        for arg_name, arg_params in args:
            if arg_name in roll_args_to_func:
                n_other_params = len(signature(roll_args_to_func[arg_name]).parameters)-1
                alias_arg_specific_roll_wrapper(code, arg_name, n_other_params, arg_params)
            else:
                alias_args_to_func = {
                    'addroll': alias_add_roll,
                }
                alias_args_to_func[arg_name](code, *arg_params)
        return '\n'.join(list(map(lambda x: parse_command(x)[0], code))), True
    elif complete_compound_dice_roll_pattern.match(command):
        return parse_compound_dice_roll(command), None
    else:
        return 'Something went wrong',

def alias_arg_specific_roll_wrapper(code, arg_name, n_other_params, params):
    if len(params) == n_other_params:
        which_roll = 0
    else:
        which_roll = int(params[-1]) - 1
        params = params[:-1]
    arg = f'{arg_name}({",".join(params)})'
    code[which_roll] = ''.join((code[which_roll], arg))


def alias_add_roll(code, new_roll):
    code.append(new_roll)


# returns
# str_to_print, alias_name_if_created, to_delete
def alias_command(command):
    try:
        second_arg = tuple(command.split(' ', 2))[1]
        if second_arg == 'delete':
            third_arg = tuple(command.split(' ', 3))[2]
            aliases.remove(third_arg)
            alias_to_code.pop(third_arg)
            return f'Removed {third_arg} from alias list', third_arg, True
        elif second_arg == 'list' or second_arg == '':
            raise IndexError()
        else:
            try:
                third_arg = tuple(command.split(' ', 2))[2]
                if third_arg == '':
                    raise IndexError()
                # dummy_run = parse_command(third_arg, True)
                # if dummy_run == "Aliases can't be nested":
                #    return dummy_run
                aliases.add(second_arg)
                alias_to_code[second_arg] = re.findall('(?:{(.*?)})', third_arg)
                return f'Added {second_arg} to alias list', second_arg
            except IndexError:
                if second_arg in aliases:
                    return f'{second_arg}: {alias_to_code[second_arg]}',
                return f'No alias {second_arg}',
    except IndexError:
        if len(aliases) == 0:
            return f'No aliases',
        return f'Aliases: {", ".join(list(aliases))}',


roll_args_to_func = {
    'add': add,
    'replace': replace,
    'adv': lambda x, y: replace(x, '2d20k1', 'd20'),
    'dis': lambda x, y: replace(x, '2d20kl1', 'd20'),
    'max': max_dice,
    'crit': max_dice,
    }


if __name__ == "__main__":
    print('Ctrl+C to terminate')
    while True:
        repl_input = input("?: ")
        print(parse_command(repl_input)[0])
        print()
