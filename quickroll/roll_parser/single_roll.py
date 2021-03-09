from random import random


class Roll:
    def __init__(self, times, sides, keep=0, is_higher =False, is_max=False, crit=False):
        self.times = times
        self.sides = sides
        self.keep = keep
        self.is_higher = is_higher
        if self.keep > self.times:
            raise ValueError("You cannot keep more rolls than are made.")
        self.clean_notation = f'{self.times}d{self.sides}'
        if self.keep != 0:
            self.clean_notation = f'{self.clean_notation}k{"l" if not self.is_higher else ""}{str(abs(self.keep))}'

        self.rolls = []
        self.roll_result = 0
        self.str = ''

        self.is_max = is_max
        self.is_crit = crit
        self.crit_bonus = self.sides * self.times if self.is_crit else 0

        self.roll()

    def roll(self):
        # the rolls are kept in a list of dicts with keys 'result' and 'kept' to leave open the opportunity
        # of seeing which rolls are kept/discarded  in case that information is needed outside the scope of this file
        # for example, in case the discarded rolls should be made a different color
        # the order is superficially important, as a roller might want to see if their advantage/disadvantage helped
        # (were the additional rolls used in the calculation or not)
        self.rolls = [{'result': self.calc_1dN(), 
                       'kept': True,} 
                      for _ in range(self.times)]
        if self.keep:
            discarded_rolls = sorted(enumerate(self.rolls),
                                    key=lambda x: x[1]['result'],
                                    reverse= not self.is_higher)
            discarded_rolls = [x[0] for x in discarded_rolls]
            for index in discarded_rolls[:self.times-abs(self.keep)]:
                self.rolls[index]['kept'] = False
        self.roll_result = sum([x['result'] for x in self.rolls if x['kept']])
        self.__str__()
        return self.roll_result + self.crit_bonus

    def result(self):
        return self.roll_result + self.crit_bonus

    def calc_1dN(self):
        return self.sides if self.is_max else int(self.sides * random() +1)

    def __str__(self):
        if not self.str:
            rolls_string_list = [str(roll['result']) for roll in self.rolls]
            self.str = f'{self.clean_notation} ({", ".join(rolls_string_list)}) {self.roll_result}'
            if self.is_crit:
                self.str = ' + '.join((self.str, str(self.crit_bonus)))
        return self.str


    def dice_images(self):
        images = []
        for roll in self.rolls:
            images.append(f'd{self.sides}_{roll["result"]}.svg')
        return images