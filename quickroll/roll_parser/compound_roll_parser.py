from re import (
    findall, fullmatch, match,
)
from .single_roll import Roll
from . import patterns

class RollEquation:
    def apply_roll_equation_args(self, args):
        for arg_name, arg_params in args:
            arg_params = [param for param in arg_params if param]
            if arg_name in self.ARGS_TO_FUNC.keys():
                if len(arg_params) == 0:
                    self.ARGS_TO_FUNC[arg_name]()
                else:
                    self.ARGS_TO_FUNC[arg_name](*arg_params)


    def __str__(self):
        equation_str = ' '.join([str(token) for token in self.tokens_with_dice])
        equation_result = self.result()
        return f'{equation_str} = {equation_result} {self.label} {self.modifiers["crit_exclamation"]}'


    def dice_image_filenames(self):
        filenames = []
        for token in self.tokens_with_dice:
            if type(token) is Roll:
                filenames.extend(token.dice_images())
        return filenames


    def is_crit(self):
        return self.modifiers['is_crit']


    def result(self):
        tokens_with_dice_result_ints = [str(token.result() if type(token) is Roll else token) for token in self.tokens_with_dice]
        return str(eval(''.join(tokens_with_dice_result_ints)))


    def add(self, extra_code):
        if extra_code[0] not in ['-+']:
            self.tokens.append('+')
        added_tokens = patterns.ROLL_EQUATION_TOKENS.findall(extra_code)
        added_tokens = [token for token in added_tokens]
        self.tokens.extend(added_tokens)


    def replace(self, repl_token, target):
        for index, token in enumerate(self.tokens):
            if fullmatch(f'(?:\d+)?{target}(?:kl?\d*)?', token):
                self.tokens[index] = repl_token


    def __init__(self, equation_str, is_crit=False):
        self.ARGS_TO_FUNC = {
            'add': self.add,
            '+': self.add,
            'replace': self.replace,
            'adv': lambda: self.replace('2d20k1', 'd20'),
            'dis': lambda: self.replace('2d20kl1', 'd20'),
            'max': lambda: self.modifiers.update({'max': True}),
            'tohit': lambda i=20: self.modifiers.update({'tohit': True, 'minimum_to_crit': int(i)}),
            'critable': lambda: self.modifiers.update({'critable': True}),
            'crit': lambda: self.modifiers.update({'is_crit': True, 'crit_exclamation': 'CRIT!'}),
        }
        self.modifiers = {
            'critable': False,
            'tohit': False,
            'minimum_to_crit': 20,
            'is_crit': is_crit,
            'crit_exclamation': '',
            'max': False,
        } 
        tokens = patterns.ROLL_COMMAND.findall(equation_str)
        args = [token[1:] for token in tokens if patterns.ARG.match(token[0])]
        args = [(arg[0], patterns.WHITESPACE.sub('', arg[1]).split(',')) for arg in args]
        self.label = next(iter([token[3] for token in tokens if patterns.ROLL_EQUATION_LABEL.match(token[0])]), '')
        self.tokens = [token[0] for token in tokens if patterns.ROLL_EQUATION_TOKENS.match(token[0])]  

        self.apply_roll_equation_args(args)
        dice_should_crit = self.modifiers['is_crit'] and self.modifiers['critable'] and not self.modifiers['tohit']
        self.tokens_with_dice = [parse_roll(token, is_max=self.modifiers['max'], crit=dice_should_crit) if fullmatch(patterns.SINGLE_ROLL, token) else token for token in self.tokens]  
        if self.modifiers['tohit']:
            d20 = next(iter([dice for dice in self.tokens_with_dice if type(dice) is Roll and dice.sides == 20]), None)
            if d20.result() >= self.modifiers['minimum_to_crit']:
                self.ARGS_TO_FUNC['crit']()


def parse_roll(token, is_max=False, crit=False):
    match = patterns.SINGLE_ROLL.match(token)
    times = int(match.group('times') or 1)
    keep = int((match.group('keep') or '0').replace('l', ''))
    is_higher = 'l' not in (match.group('keep') or '')
    sides = int(match.group('sides'))
    return Roll(times, sides, keep, is_higher, is_max, crit)
