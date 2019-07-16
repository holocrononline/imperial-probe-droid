#!/usr/bin/python3

import json
from config import load_config
from swgohhelp import fetch_players

config = load_config()
ally_codes = [ 349423868 ]
project = {
	'allycodes': ally_codes,
	'project': {
		'allyCode': 1,
		'roster': {
			'defId': 1,
			'stats': 1,
		},
	},
}

result = fetch_players(config, project)
print(json.dumps(result, indent=4))
