from opts import *
from errors import *
from utils import http_get, translate

from swgohgg import get_full_avatar_url
from swgohhelp import fetch_players, get_ability_name

import DJANGO
from swgoh.models import BaseUnit, BaseUnitSkill

help_zeta = {
	'title': 'Zeta Help',
	'description': """Shows zeta abilities activated for a player.

**Syntax**
```
%prefixzeta [unit]```
**Aliases**
```
%prefixz```

**Examples**
Show activated zeta abilities of all your units:
Show activated zeta abilities of Count Dooku:
```
%prefixzeta dooku```"""
}

def is_zetad(skill_id, player_unit):

	if 'skills' in player_unit:
		for skill in player_unit['skills']:
			if skill['id'] == skill_id:
				return skill['tier'] == 8 and '✅' or '❎'

	return '❎'

def get_zetas(config, ref_unit, player_unit, language):

	result = {}

	base_id = ref_unit.base_id
	unit = BaseUnit.objects.get(base_id=base_id)
	zetas = BaseUnitSkill.objects.filter(unit_id=unit.id, is_zeta=1)
	for zeta in zetas:

		zeta_name = get_ability_name(config, zeta.skill_id, language)
		unit_name = ref_unit.name
		if unit_name not in result:
			result[unit_name] = {
				'zetas': {}
			}

		result[unit_name]['url'] = ref_unit.get_url()
		result[unit_name]['translated'] = translate(ref_unit.base_id, language)
		result[unit_name]['zetas'][zeta_name] = is_zetad(zeta.skill_id, player_unit)

	return result

def cmd_zeta(config, author, channel, args):

	language = parse_opts_lang(author)

	args, selected_players, error = parse_opts_players(config, author, args, min_allies=1, max_allies=1)

	args, selected_units = parse_opts_unit_names(config, args)

	if args:
		return error_unknown_parameters(args)

	if error:
		return error

	ally_code = selected_players[0].ally_code
	players = fetch_players(config, {
		'allycodes': [ ally_code ],
		'project': {
			'allyCode': 1,
			'name': 1,
			'roster': {
				'defId': 1,
				'gear': 1,
				'level': 1,
				'rarity': 1,
				'skills': 1,
				'equipped': {
					'slot': 1,
				},
			},
		},
	})


	msgs = []
	for ally_code_str, player in players.items():
		for ref_unit in selected_units:

			lines = []
			fields = []
			player_unit = ref_unit.base_id in player['roster'] and player['roster'][ref_unit.base_id] or {}
			zetas = get_zetas(config, ref_unit, player_unit, language)
			for name, data in zetas.items():
				lines.append('**[%s](%s)**' % (data['translated'], ref_unit.get_url()))
				lines.append('%s' % config['separator'])
				for zeta, status in data['zetas'].items():
					lines.append('`%s %s`' % (status, zeta))

			msgs.append({
				'title': '',
				'description': '\n'.join(lines),
				'author': {
					'name': ref_unit.name,
					'icon_url': ref_unit.get_image(),
				},
				'image': get_full_avatar_url(config, ref_unit.image, player_unit),
				'fields': fields,
			})

	return msgs
