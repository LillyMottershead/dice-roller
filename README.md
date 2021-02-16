## dice_roller

# About

This is a lightweight dice roller script, which helps players perform rolls and calculations quickly. It includes a basic aliasing system, which allows for quickly and easily creating sets of rolls.

# Dependencies

Dice Roller requires Python >= 3.8.0

# Usage

Dice Roller must currently be run off the command line from python. Run dice_parser.py for a simple command line interface, or gui.py for a simple gui.

A basic dice roll can be done by typing:

'd20'
'd6+6'

The roller supports basic math with +-*/() operators.
Dice mechanics like advantage or disadvantage can be done using keep notation:

'2d20k1' adv
'2d20kl1' dis

Or, more readably:

'd20 adv'
'd20 dis'

An alias can be created with a single roll:

'alias name {d20}'

Or with multiple rolls:

'alias name {d20} {d6+3}'