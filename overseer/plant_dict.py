plant_dict = {
    'Rosemary':         {'scientific_name': 'Salvia rosmarinus',   'type': 'herb',       'state': 'plant',  'position': '%[75,100]',    'water_info' : {'type':'POINT', 'amount' : 8, 'schedule': 'week', 'freq': 1}, 'present': 'yes'},
    'Gold-Leaf-Thyme':  {'scientific_name': 'Thymus citriodorus',  'type': 'herb',       'state': 'plant',  'position': '%[85,50]',     'water_info' : {'type':'POINT', 'amount' : 8, 'schedule': 'week', 'freq': 2}, 'present': 'yes'},
    'Sage':             {'scientific_name': 'Salvia officinalis',  'type': 'herb',       'state': 'plant',  'position': '%[75,100]',    'water_info' : {'type':'POINT', 'amount' : 4, 'schedule': 'week', 'freq': 2}, 'present': 'yes'},
    'Shishito-Peppers': {'scientific_name': 'Capsicum annuum',     'type': 'pepper',     'state': 'seed',   'position': '%[65,50]',     'water_info' : {'type':'CIRCLE', 'radius': 50, 'angle': [0,360], 'amount' : 4, 'schedule': 'week', 'freq': 2}, 'present': 'yes'},
    'Jade-Plant':       {'scientific_name': 'Crassula ovata',      'type': 'succulent',  'state': 'plant',  'position': '%[0,0]',       'water_info' : {'type':'POINT', 'amount' : 4, 'schedule': 'week', 'freq': 2},  'present': 'yes'},
    'Ponthos':          {'scientific_name': 'Epipremnum aureum',   'type': 'plant (wet)','state': 'plant',  'position': '%[100,100]',   'water_info' : {'type':'POINT', 'amount' : 8, 'schedule': 'week', 'freq': 2}, 'present': 'yes'},
    'Chives':           {'scientific_name': 'Allium schoenoprasum','type': 'herb',       'state': 'plant',  'position': '%[35,50]',     'water_info' : {'type':'LINE', 'start':'%[33,0]', 'end': '%[37,100]', 'amount' : 3, 'schedule': 'week', 'freq': 2}, 'present': 'yes'},
    'Lavendar':         {'scientific_name': 'Lavandula stoehas',   'type': 'herb',       'state': 'plant',  'position': '%[20,50]',     'water_info' : {'type':'LINE', 'start':'%[20,0]', 'end': '%[20,100]', 'amount' : 3, 'schedule': 'week', 'freq': 2}, 'present': 'yes'},
    'Parsley':          {'scientific_name': 'Petroselinum crispum','type': 'herb',       'state': 'plant',  'position': '%[9,50]',      'water_info' : {'type':'LINE', 'start':'%[9,0]', 'end': '%[9,100]', 'amount' : 3, 'schedule': 'week', 'freq': 2}, 'present': 'yes'},
    'Basil':            {'scientific_name': 'Ocimum basilicum',    'type': 'herb',       'state': 'plant',  'position': '%[55,0]',      'water_info' : {'type':'POINT',  'amount' : 3, 'schedule': 'week', 'freq': 3}, 'present': 'yes'},
    'Spearmint':        {'scientific_name': 'Mentha spicata',      'type': 'herb',       'state': 'plant',  'position': '%[55,100]',    'water_info' : {'type':'POINT',  'amount' : 3, 'schedule': 'week', 'freq': 3}, 'present': 'yes'},
}
    #'Chives':           {'scientific_name': 'Epipremnum aureum',   'type': 'plant',      'state': 'plant',  'position': '[%[35,0-100), %(40,100)]',    'water_schedule': ('day'  ,1),  'water_amount': 8,  'present': 'yes'},
    #'Lavendar':         {'scientific_name': 'Epipremnum aureum',   'type': 'plant',      'state': 'plant',  'position': '[%[20,0-100), %(24,0-100)]',    'water_schedule': ('day'  ,1),  'water_amount': 8,  'present': 'yes'},
    #'Parsley':          {'scientific_name': 'Epipremnum aureum',   'type': 'plant',      'state': 'plant',  'position': '[%[9,0-100), %(5,0-100)]',
