from .dice import Dice
import re


blank_space_pattern = re.compile(r'(\s*)')
single_dice_roll_pattern = re.compile(r'(?P<times>\d+)?d(?P<sides>\d+)(?:k(?P<keep>[l-]?\d*))?')
valid_tokens = {'dice_roll': r'(?:(?:\d+)?d\d+(?:kl?\d*)?)',
                'math_operator': r'(?:[+\-*/()])',
                'number': r'(?:\d+)',
                'label': r'(?:\[[\w\s]*\])',
                'adv': r'(?:adv)',
                'dis': r'(?:dis)'}
valid_compound_tokens_pattern = re.compile('(' + '|'.join(valid_tokens.values()) + ')')
complete_compound_dice_roll_pattern = re.compile('(' + '|'.join(valid_tokens.values()) + r'|(?:\s))+')
args_pattern = re.compile(r'(?:(\w+)(?:\((.*?)\))?)')

aliases = set()
alias_to_code = {}


def parse_single_dice_roll(token):
    match = re.match(single_dice_roll_pattern, token)
    times = int(match.group('times')) if match.group('times') is not None else 1
    keep = int(match.group('keep').replace('l', '-')) if match.group('keep') is not None else 0
    return Dice(times, int(match.group('sides')), keep)


def parse_compound_dice_roll(compound_dice_roll):
    tokens = re.findall(valid_compound_tokens_pattern, compound_dice_roll)
    if 'dis' in tokens:
        d20_index, _ = next(enumerate([token for token in tokens if 'd20' in token]))
        tokens[d20_index] = '2d20kl1'
        tokens.remove('dis')
    if 'adv' in tokens:
        d20_index, _ = next(enumerate([token for token in tokens if 'd20' in token]))
        tokens[d20_index] = '2d20k1'
        tokens.remove('adv')
    try:
        label = list(filter(lambda x: re.match(valid_tokens['label'], x) is not None, tokens))[0]
        tokens = list(filter(lambda x: re.match(valid_tokens['label'], x) is None, tokens))
    except IndexError:
        label = ''
    tokens_with_dice_objects = list(map(lambda x: parse_single_dice_roll(x) if re.fullmatch(single_dice_roll_pattern, x) else x, tokens))
    tokens_with_dice_result_strings = list(map(str, tokens_with_dice_objects))
    tokens_with_dice_result_ints = list(map(lambda x: str(x.result) if type(x) is Dice else x, tokens_with_dice_objects))
    return ' '.join(tokens_with_dice_result_strings) + ' = ' + str(eval(''.join(tokens_with_dice_result_ints))) + ' ' + label[1:-1]


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
            alias_args_to_func = {'add': add,
                                  'addroll': add_roll,
                                  'replace': replace,
                                  'adv': lambda x, y: replace(x, '2d20k1', 'd20', y),
                                  'dis': lambda x, y: replace(x, '2d20kl1', 'd20', y),
                                  'max': max_dice,
                                  'crit': max_dice}
            alias_args_to_func[arg_name](code, *arg_params)
        return '\n'.join(list(map(lambda x: parse_command(x)[0], code))), True
    elif match := re.match(complete_compound_dice_roll_pattern, command):
        return parse_compound_dice_roll(match.group()), None
    else:
        return 'Something went wrong'


def add(code, extra_code, roll=1):
    roll = int(roll)-1
    if extra_code[0] not in ['-+']:
        extra_code = '+' + extra_code
    code[roll] = ''.join((code[roll], extra_code))


def add_roll(code, new_roll):
    code.append(new_roll)


def replace(code, repl_code, target, roll=1):
    if roll == '':
        roll = 1
    roll = int(roll)-1
    code[roll] = re.sub(f'(?:\d+)?{target}(?:kl?\d*)?', repl_code, code[roll])


def max_dice(code, roll=1):
    if roll == '':
        roll = 1
    roll = int(roll)-1
    tokens = re.findall(valid_compound_tokens_pattern, code[roll])
    tokens = list(map(lambda x: str((int(times) if (times := match.group('times')) else 1)*int(match.group('sides'))) if (match := single_dice_roll_pattern.fullmatch(x)) else x, tokens))
    joined_tokens = ''.join(tokens)
    code[roll] = ''.join(tokens)
    return joined_tokens


def parse_command_tuple_wrapper(command):
    result = parse_command(command)
    if type(result) != tuple:
        return result, None
    return result


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
                    return f'{second_arg}: {alias_to_code[second_arg]}'
                return f'No alias {second_arg}'
    except IndexError:
        if len(aliases) == 0:
            return f'No aliases'
        return f'Aliases: {", ".join(list(aliases))}'


if __name__ == "__main__":
    while True:
        repl_input = input("?: ")
        if repl_input == 'q':
            exit()
        print(parse_command(repl_input)[0])
