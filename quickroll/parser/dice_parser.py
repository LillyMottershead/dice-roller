from inspect import signature
from re import (
    findall, fullmatch, match,
)
import parser_regex as PATTERNS
from compound_roll_parser import (
    parse_compound_dice_roll, ARGS_TO_FUNC
)

aliases = set()
alias_to_code = {}

def parse_command(command, inner=False):
    first_arg = tuple(command.split(' ', 1))[0]
    if first_arg == 'alias':
        return alias_command(command)
    elif first_arg in aliases:
        code = alias_to_code[first_arg].copy()
        try:
            second_arg = tuple(command.split(' ', 1))[1]
            args = PATTERNS.COMPOUND_ARG.findall(second_arg)
            args = list(map(lambda x: (x[0], PATTERNS.WHITESPACE.sub('', x[1]).split(',')), args))
        except IndexError:
            args = []
        for arg_name, arg_params in args:
            if arg_name in ARGS_TO_FUNC:
                n_other_params = len(signature(ARGS_TO_FUNC[arg_name]).parameters)-1
                alias_arg_specific_roll_wrapper(code, arg_name, n_other_params, arg_params)
            else:
                alias_args_to_func = {
                    'addroll': alias_add_roll,
                }
                alias_args_to_func[arg_name](code, *arg_params)
        result = []
        is_crit = False
        for roll in code:
            roll_result = parse_compound_dice_roll(roll, is_crit)
            result.append(roll_result[0])
            is_crit = roll_result[1] or is_crit
        return '\n'.join(result), True
    elif PATTERNS.COMPLETE_COMPOUND_ROLL.match(command):
        return parse_compound_dice_roll(command, False)[0], None
    else:
        return 'Something went wrong',

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
                alias_to_code[second_arg] = findall('(?:{(.*?)})', third_arg)
                return f'Added {second_arg} to alias list', second_arg
            except IndexError:
                if second_arg in aliases:
                    return f'{second_arg}: {alias_to_code[second_arg]}',
                return f'No alias {second_arg}',
    except IndexError:
        if len(aliases) == 0:
            return f'No aliases',
        return f'Aliases: {", ".join(list(aliases))}',


if __name__ == "__main__":
    print('Ctrl+C to terminate')
    while True:
        repl_input = input("?: ")
        print(parse_command(repl_input)[0])
        print()
