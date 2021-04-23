## Quick Roll

# About

This is a lightweight dice roller script, which helps players perform rolls and calculations quickly. It includes a basic aliasing system, which allows for quickly and easily creating sets of rolls.

# Usage

See https://lillymottershead.github.io/quick-dice/ to use the app! Try typing `d20` in the text bar at the top and press enter (or the > button).

Now try making the roll more complicated with `d20+d4+7`.

If you wanted to make that roll three separate times, type it in again, and then type `3` in the smaller text bar adjacent to it and press enter.

Want advantage or disadvantage? Try `d20+7 adv` (use `dis` for disadvantage). This is the easiest way, but if you wanted to do it in the dice notation way you can also type `2d20k1+7`.

Maybe you want to roll damage, and make a little note as to what type of damage it is. You can do `8d6 [fire]`, and see what happens. If you wanted to do that several times quickly, you could set an alias with `alias fireball {8d6 [fire]}`. Now try typing `fireball` in the command bar.

Now lets use that alias to create an attack. Type in `alias eldritch-blast {d20+5 [to hit]} {d10+3 [force]} attack`. Keep in mind that alias names can't have white space in them. The attack parameter at the end sets up the alias to allow crits. Now type `eldritch-blast` and press enter. You can also try `eldritch-blast dis` to make the attack at disadvantage or `eldritch-blast crit` to auto crit. Mouseover the dice rolls if you want to see the math, or check the log. If you need to add hex damage to it: `eldritch-blast {d6 [necrotic] cancrit}`. The cancrit parameter allows crit damage to be calculated on that roll. Maybe you've been baned, do `eldritch-blast add(-d4)`. This will add `-d4` to the first roll calculation (in this case, the d20 roll to hit). You can specify which roll to apply these parameters to like this: `eldritch-blast add(d4, 2)`. This will add a `+d4` to the second roll calculation.

Made a mistake with your alias? You can simply overwrite it or you can remove it with `alias delete name-of-alias`.