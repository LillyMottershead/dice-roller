from inspect import signature
from re import (
    findall, fullmatch, match,
)
from . import patterns
from .compound_roll_parser import (
    RollEquation
)
from .decorators import ensure_tuple_return

aliases = set()
alias_to_code = {}

@ensure_tuple_return
def parse_command(command, inner=False):
    if patterns.COMPLETE_ROLL_EQUATION.match(command):
        return RollEquation(command)
        # return str(roll), roll.dice_image_filenames()

    command_iter = iter(command.split(' '))
    if not command_iter:
        return
    front_token = next(command_iter)
    
    if front_token == 'load':
        return load(next(command_iter, ''))
    elif front_token == 'save':
        return save_aliases(next(command_iter, ''))
    elif front_token == 'alias':
        return alias_command(command_iter)
    elif front_token in aliases:
        return tuple(call_alias(front_token, command_iter))
    else:
        return f'Unknown command {front_token}'


# returns
# str_to_print, dice_image_names
@ensure_tuple_return
def alias_command(command):
    def alias_list():
        if len(aliases) == 0:
            return f'No aliases'
        return f'Aliases: {", ".join(list(aliases))}'
    front_token = ''
    try:
        front_token = next(command)
    except StopIteration:
        return alias_list()
    if front_token == 'delete':
        try:
            to_delete = next(command)
        except StopIteration:
            return 'Missing alias in alias delete <target_alias>'
        aliases.remove(to_delete)
        alias_to_code.pop(to_delete)
        return f'Removed {to_delete} from alias list', to_delete, True
    elif front_token == 'list':
        return alias_list()
    else:
        remaining = ' '.join(command)
        if not remaining:
            if front_token in aliases:
                return f'{front_token}: {alias_to_code[front_token]}'
            else:
                return f'No alias {front_token}'
        # dummy_run = parse_command(front_token, True)
        # if dummy_run == "Aliases can't be nested":
        #    return dummy_run
        aliases.add(front_token)
        code = findall(patterns.ALIAS_COMMAND, remaining)
        rolls = [roll[0] for roll in code if fullmatch(patterns.ALIAS_ROLL, roll[0])]
        rolls = [roll[1:-1] for roll in rolls]
        args = [roll[2:] for roll in code if not fullmatch(patterns.ALIAS_ROLL, roll[0])]
        parse_alias_args(rolls, args)
        alias_to_code[front_token] = rolls
        return f'Added {front_token} to alias list'


def call_alias(alias_name, command):
    roll_commands = alias_to_code[alias_name].copy()
    command = ' '.join([token for token in command])
    args = patterns.ARG.findall(command)
    args = list(map(lambda x: (x[0], patterns.WHITESPACE.sub('', x[1]).split(',')), args))
    parse_alias_args(roll_commands, args)
    is_crit = False
    rolls = []
    for roll_command in roll_commands:
        roll = RollEquation(roll_command, is_crit)
        is_crit = roll.is_crit() or is_crit
        rolls.append(roll)
    return rolls
    # for roll_command in rolls:
    #     roll = RollEquation(roll_command, is_crit)
    #     roll_result = str(roll)
    #     dice_images.extend(roll.dice_image_filenames())
    #     result.append(roll_result)
    #     is_crit = roll_result[1] or is_crit
    # return '\n'.join(result), dice_images


def parse_alias_args(code, args):
    def alias_arg_specific_roll_wrapper(code, arg_name, n_other_params, params):
        if len(params) == n_other_params:
            which_roll = 0
        else:
            which_roll = int(params[-1] or 1) - 1
            params = params[:-1]
        arg = f'{arg_name}({",".join(params)})'
        code[which_roll] = ' '.join((code[which_roll], arg))

    def alias_add_roll(code, new_roll):
        code.append(new_roll)

    def set_attack(code, *critable_rolls):
        if critable_rolls:
            critable_rolls = [int(x) for x in critable_rolls]
        else:
            critable_rolls = range(1, len(code))
        code[0] = code[0] + ' tohit'
        for i in critable_rolls:
            code[i] = code[i] + ' critable'

    ARGS_TO_FUNC_PARAM_N = {
                'add': 1,
                '+': 1,
                'replace': 2,
                'adv': 2,
                'dis': 2,
                'max': 0,
                'tohit': 1,
                'critable': 0,
                'crit': 0,
            }
    for arg_name, arg_params in args:
        if arg_name in ARGS_TO_FUNC_PARAM_N:
            n_other_params = ARGS_TO_FUNC_PARAM_N[arg_name]
            alias_arg_specific_roll_wrapper(code, arg_name, n_other_params, arg_params)
        else:
            alias_args_to_func = {
                'addroll': alias_add_roll,
                'attack': set_attack,
            }
            alias_args_to_func[arg_name](code, *arg_params)


def load(filename):
    with open(filename) as file:
        for line in file.readlines():
            parse_command(line)
    return f'Loaded {filename}'


def save_aliases(filename):
    def format_alias_code(rolls):
        rolls_with_curlies = [f'{{{roll}}}' for roll in rolls]
        return ' '.join(rolls_with_curlies)
    
    f = open(filename, 'w')
    for alias, rolls in alias_to_code.items():
        f.write(f'alias {alias} {format_alias_code(rolls)}\n')
    f.close()
    return f'Exported to {filename}'