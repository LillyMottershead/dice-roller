from random import random


class Dice:
    def __init__(self, times, sides, keep=0):
        self.times = int(times)
        self.sides = int(sides)
        self.lower = keep < 0
        self.keep = abs(int(keep))
        self.clean_notation = f'{self.times}d{self.sides}'
        if self.keep != 0:
            self.clean_notation = f'{self.clean_notation}k{"l" if self.lower else ""}{str(abs(self.keep))}'

        self.rolls = []
        self.result = 0
        self.str = ''
        self.roll()

    def roll(self):
        # the rolls are kept in a list of dicts with keys 'result' and 'kept' to leave open the opportunity
        # of seeing which rolls are kept/discarded  in case that information is needed outside the scope of this file
        # for example, in case the discarded rolls should be made a different color
        # the order is superficially important, as a roller might want to see if their advantage/disadvantage helped
        # (were the additional rolls used in the calculation or not)
        self.rolls = [{'result': int(self.sides * random() + 1), 
                    'kept': True,} 
                    for _ in range(self.times)]
        if self.keep != 0:
            discarded_rolls = sorted(enumerate(self.rolls),
                                    key=lambda x: x[1]['result'],
                                    reverse=self.lower)
            discarded_rolls = [x[0] for x in discarded_rolls]
            for index in discarded_rolls[:self.times-abs(self.keep)]:
                self.rolls[index]['kept'] = False
        self.result = sum([x['result'] for x in self.rolls if x['kept']])
        self.__str__()
        return self.result

    def __str__(self):
        if not self.str:
            rolls_string_list = [str(roll['result']) for roll in self.rolls]
            self.str = f'{self.clean_notation} ({", ".join(rolls_string_list)}) {self.result}'
        return self.str
            