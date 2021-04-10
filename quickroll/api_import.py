import requests

BASE_URL = 'https://www.dnd5eapi.co/api/monsters/'


def get_monster(monster_name):
    monster = requests.get(f'{BASE_URL}{monster_name}')
    if monster.status_code == 200:
        return monster.json()
    return f'{monster.status_code} error'

def get_monster_actions(monster_json):
    actions = []
    for action in monster_json['actions']:
        name = action['name'].lower().replace(' ', '-')
        if 'attack_bonus' in action:
            to_hit = f'{{d20+{action["attack_bonus"]} [to hit]}}'
            damages = []
            for damage in action['damage']:
                damage = f'{{{damage["damage_dice"]} [{damage["damage_type"]["index"]}]}}'
                damages.append(damage)
            action = f'{name} {to_hit} {" ".join(damages)}'
            actions.append(action)
    return actions
        

import sys
if __name__ == "__main__":
    monster_json = get_monster(sys.argv[1])
    print([x for x in get_monster_actions(monster_json)])
