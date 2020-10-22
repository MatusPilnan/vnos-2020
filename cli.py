import asyncio
import glob

import colorama
import pyfiglet
from PyInquirer import prompt
from pybeerxml.parser import Parser
from pybeerxml.recipe import Recipe
from termcolor import colored

pyfiglet.print_figlet('Var:Pivo', font='basic', colors='YELLOW:DEFAULT')
colorama.init()
MASH = 1
BOIL = 2
steps = ['Mash', 'Boil']


def get_filenames(path='', extension='.mp3'):
    if path[-1] == '/' or path[-1] == '\\':
        path = path + '*' + extension
    elif len(path) > 0:
        path = path + '/*' + extension

    filenames = glob.glob(pathname=path)
    result = [filename for filename in filenames]
    result.sort()
    return result


def confirm_manual_step(message, default=False):
    return prompt({'type': 'confirm', 'name': 'ok', 'message': message, 'default': default})['ok']


def print_ingredients(recipe: Recipe, step=None):
    print('INGREDIENTS:')
    if step is None:
        pyfiglet.print_figlet(f'{"HOPS":-^15}', font='digital')
        for hop in recipe.hops:
            print(f'{hop.name} - {(hop.amount * 1000):.2f} g - {hop.use}')
        print('\n')
        pyfiglet.print_figlet(f'{"FERMENTABLES":-^15}', font='digital')
        for fermentable in recipe.fermentables:
            print(f'{fermentable.name} - {fermentable.amount:.2f} kg')
        print('\n')
        pyfiglet.print_figlet(f'{"YEASTS":-^15}', font='digital')
        for yeast in recipe.yeasts:
            print(f'{yeast.name} - {yeast.amount * 1000:.2f} g')
        print('\n')
        pyfiglet.print_figlet(f'{"MISCELLANEOUS":-^15}', font='digital')
        for misc in recipe.miscs:
            print(f'{misc.name} - {misc.amount:.2f} - {misc.use}')
    elif step == MASH:
        for f in recipe.fermentables:
            # print(f.add_after_boil)
            if not f.add_after_boil:
                print(f'{f.name} - {f.amount:.2f} kg')


def prepare_recipe_files(recipe_files):
    for file in recipe_files:
        with open(file) as f:
            content = f.read()

        content = content.replace('>true<', '>1<').replace('>TRUE<', '>1<')
        content = content.replace('>false<', '>0<').replace('>FALSE<', '>0<')

        with open(file, 'w') as f:
            f.write(content)


async def change_temp(target):
    print(f'Changing temperature to {target}...')
    await asyncio.sleep(5)
    print(f'Temperature is {target}!')


async def weigh(ingredients, confirm=False):
    weighing = True
    if confirm:
        weighing = confirm_manual_step('Do you need to weigh your fermentables?', True)
    if not weighing:
        return False
    for ing in ingredients:
        print(f'Weighing {ing.amount} of {ing.name}...')
        await asyncio.sleep(7)
        print(f'Weight: {ing.amount}!')


async def follow_mash_steps(mash_steps, fermentables):
    weighing = None
    for i, ms in enumerate(mash_steps):
        print(colored(f'Mashing step {i + 1}/{len(mash_steps)}: {ms.name}', attrs=['bold']))
        print(f'({ms.step_temp:.2f}C for {ms.step_time:.0f} min.)')
        while not confirm_manual_step(f'Add {ms.infuse_amount:.2f} L of water.'):
            print('You need to add water to continue!')
        if weighing is None:
            weighing = await asyncio.gather(change_temp(ms.step_temp), weigh(fermentables, confirm=True))


files = get_filenames('./recipes', extension='.xml')
prepare_recipe_files(files)
parser = Parser()
recipe_choices = []
for file in files:
    recipes = parser.parse(file)
    for r in recipes:
        recipe_choices.append({'name': f'{r.name} (by {r.brewer})', 'value': r})

answers = prompt([{'type': 'list', 'name': 'recipe', 'message': 'Select a recipe to brew', 'choices': recipe_choices}])

recipe: Recipe = answers['recipe']
print(f"Let's brew {recipe.name}!\nIngredients list:")
print_ingredients(recipe)

print(f'=======================')
print(colored(f'MASHING: {len(recipe.mash.steps)} step(s)', color='yellow', attrs=['bold']))
print(f'=======================')
print_ingredients(recipe, step=MASH)

asyncio.run(follow_mash_steps(recipe.mash.steps, recipe.fermentables))
