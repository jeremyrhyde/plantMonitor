from apscheduler.schedulers.background import BackgroundScheduler
from util import Logger
from overseer.plant_dict import *
import math

def print_test(logger, plant_key):
    present = plant_dict[plant_key]['present']
    pos = plant_dict[plant_key]['position']
    water_amount = plant_dict[plant_key]['water_amount']
    logger.info('Watering {} - at positon: {}, water_amount: {}'.format(plant_key, pos, water_amount))

def user_input():
    print("\nOptions: WATER / ETC")

    user_option = input("Enter option: ").upper()

    print("User command input - {}".format(user_option))

    return user_option

logger = Logger('temp.log')

# Initialize overseer
overseer_id = '0'
overseer_logger = logger.init('OVERSEER', overseer_id)
sched = BackgroundScheduler(daemon=True)

i = 0
key_list = []
for key in plant_dict:
    key_list.append(key)
    print('Scheduling job [{}]'.format(i))
    sched.add_job(print_test, 'cron', minute=12, second='{}'.format(i*5), args=[overseer_logger, key_list[i]], id='{} job'.format(key_list[i]))
    i = i +1


sched.start()
while True:
    inp = user_input()

    sched.print_jobs()
