import random


class Dice:
    def __init__(self, times, sides, keep=0):
        self.all_rolls = {index: int(random.random() * sides) + 1 for index in range(int(times))}
        self.kept_roll_indices = {index: True for index in range(len(self.all_rolls))}
        self.result = 0
        self.clean_notation = f'{times}d{sides}'
        if keep != 0:
            self.clean_notation = self.clean_notation + 'k' + (str(keep) if keep > 0 else 'l' + str(abs(keep)))
        self.__times__ = times
        self.__sides__ = sides
        self.__keep__ = keep

        if self.__keep__ == 0:
            self.result = sum(self.all_rolls.values())
        else:
            sorted_tuples = sorted([(key, element) for (key, element) in self.all_rolls.items()],
                                   key=lambda x: x[1],
                                   reverse=(self.__keep__ > 0))
            self.kept_roll_indices = {index: False for index in range(len(self.all_rolls))}
            for (index, _) in sorted_tuples[:abs(self.__keep__)]:
                self.kept_roll_indices[index] = True
            summing = [roll for (roll, kept) in zip(self.all_rolls.values(),
                                                    self.kept_roll_indices.values()) if kept]
            self.result = sum(summing)

        rolls_info = zip(self.all_rolls.values(), self.kept_roll_indices.values())
        rolls_string_list = [str(roll) for roll, kept in rolls_info]
        self.str = f'{self.clean_notation} ({", ".join(rolls_string_list)}) {self.result}'

    def __str__(self):
        return self.str