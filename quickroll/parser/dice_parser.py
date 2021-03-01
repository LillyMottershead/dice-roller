from inspect import signature
from re import (
    findall, fullmatch, match,
)
import parser_regex as PATTERNS
from compound_roll_parser import (
    parse_roll_equation, ARGS_TO_FUNC
)

aliases = set()
alias_to_code = {}


def parse_command(command, inner=False):
    first_arg = tuple(command.split(' ', 1))[0]
    if first_arg == 'alias':
        return alias_command(command),
    if first_arg == 'load':
        return load(command.split(' ', 1)[1]),
    elif first_arg in aliases:
        code = alias_to_code[first_arg].copy()
        try:
            second_arg = tuple(command.split(' ', 1))[1]
            args = PATTERNS.ARG.findall(second_arg)
            args = list(map(lambda x: (x[0], PATTERNS.WHITESPACE.sub('', x[1]).split(',')), args))
        except IndexError:
            args = []
        parse_alias_args(code, args)
        result = []
        is_crit = False
        for roll in code:
            roll_result = parse_roll_equation(roll, is_crit)
            result.append(roll_result[0])
            is_crit = roll_result[1] or is_crit
        return '\n'.join(result), True
    elif PATTERNS.COMPLETE_ROLL_EQUATION.match(command):
        return parse_roll_equation(command, False)[0], None
    else:
        return 'Something went wrong',

def parse_alias_args(code, args):
    for arg_name, arg_params in args:
        if arg_name in ARGS_TO_FUNC:
            n_other_params = len(signature(ARGS_TO_FUNC[arg_name]).parameters)-2
            alias_arg_specific_roll_wrapper(code, arg_name, n_other_params, arg_params)
        else:
            alias_args_to_func = {
                'addroll': alias_add_roll,
                'attack': set_attack,
            }
            alias_args_to_func[arg_name](code, *arg_params)


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
                code = findall(PATTERNS.ALIAS_COMMAND, third_arg)
                rolls = [roll[0] for roll in code if fullmatch(PATTERNS.ALIAS_ROLL, roll[0])]
                args = [roll[2:] for roll in code if not fullmatch(PATTERNS.ALIAS_ROLL, roll[0])]
                parse_alias_args(rolls, args)
                alias_to_code[second_arg] = rolls
                return f'Added {second_arg} to alias list', second_arg
            except IndexError:
                if second_arg in aliases:
                    return f'{second_arg}: {alias_to_code[second_arg]}',
                return f'No alias {second_arg}',
    except IndexError:
        if len(aliases) == 0:
            return f'No aliases',
        return f'Aliases: {", ".join(list(aliases))}',


def load(filename):
    with open(filename) as file:
        for line in file.readlines():
            parse_command(line)
    return f'Loaded {filename}'



if __name__ == "__main__":
    print('Ctrl+C to terminate')
    while True:
        repl_input = input("?: ")
        print(parse_command(repl_input)[0])
        print()
