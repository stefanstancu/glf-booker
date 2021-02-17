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


no_auth = False
s = requests.Session()
# Auth
# Check for valid cookies
if os.path.exists(cookie_fp):
    with open(cookie_fp, 'rb') as f:
        s.cookies.update(pickle.load(f))

    expiry = next(x for x in s.cookies if x.name == 'secureLoginToken').expires
    if time.time() < expiry:
        no_auth = True

if not no_auth:
    r = s.post(auth_url, {'login': cred.user, 'passwordParameter': cred.password})
    print(f'login: {r.status_code}')

# Request workout slot list
date = (datetime.now() + timedelta(days=6)).strftime("%Y-%m-%d")
url = f_url(337, date) # just the one club for now
r = s.get(url)
slots = r.json()['map']['response'][0]['workouts']

# Book the workout
# book from the 3rd time slot down, depending on availability
for time_slot_id in [x['identifier'] for x in (slots[3:] + slots[:3])]:
    r = s.post(book_url, {'clubId': 337, 'timeSlotId': time_slot_id})
    if r.status_code != 200:
        print(r.json()['map']['response']['message'])
    else:
        break

# Save the cookie
if not no_auth:
    with open(cookie_fp, 'wb+') as f:
        pickle.dump(s.cookies, f)

s.close()
