import requests
import json
import cred
import os
import pickle

import time
from datetime import datetime, timedelta

cookie_fp = 'cookies.ck'
clubs = ['337', '351', '257']
auth_url = 'https://www.goodlifefitness.com/content/experience-fragments/goodlife/header/master/jcr:content/root/responsivegrid/header.AuthenticateMember.json'
book_url = 'https://www.goodlifefitness.com/content/goodlife/en/book-workout/jcr:content/root/responsivegrid/workoutbooking.CreateWorkoutBooking.json'

def f_url(club: str, date: str):
    """ date should be in YYYY-MM-DD format
    """
    return f'https://www.goodlifefitness.com/content/goodlife/en/book-workout/jcr:content/root/responsivegrid/workoutbooking.GetWorkoutSlots.{club}.{date}.json'


print('Running at ' + str(datetime.now()))
no_auth = False
s = requests.Session()
# Auth
r = s.post(auth_url, {'login': cred.user, 'passwordParameter': cred.password})
print(f'login: {r.status_code}')

# Request workout slot list
date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
url = f_url(337, date) # just the one club for now
r = s.get(url)
slots = r.json()['map']['response'][0]['workouts']

# Book the workout
# book from the 3rd time slot down, depending on availability
delay = 1
for time_slot_id in [x['identifier'] for x in (slots[3:] + slots[:3])]:
    r = s.post(book_url, {'clubId': 337, 'timeSlotId': time_slot_id})
    print(f'attemping to book @ {str(datetime.now())} in {delay}s intervals ...')
    cnt = 0
    while r.status_code != 200 and cnt < 200:
        r = s.post(book_url, {'clubId': 337, 'timeSlotId': time_slot_id})
        cnt += 1
        print(f'attempt: {r.json()}')
        time.sleep(delay)
    print('successfully booked:' + str(r.json()))
    break

s.close()
