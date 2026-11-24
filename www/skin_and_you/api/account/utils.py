import os
import random
import os, uuid, requests

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


from skin_and_you import settings

def download_image(download_link):
    response = requests.get(download_link)
    random_name = uuid.uuid4().hex + ".png"
    folder_name = "profile"
    
    absolute_file_path = os.path.join(settings.MEDIA_ROOT, folder_name, random_name)
    relative_path = os.path.join(folder_name, random_name)
    with open(absolute_file_path, 'wb') as f:
        f.write(response.content)
    
    print("Relative Path == ", relative_path)
    return relative_path

    
    
def get_date_range_by_entity(title):
    if not title in ['today', 'yesterday','tomorrow','this_week','this_month']:
        return False
    
    date_range =  {}
    
    if title == "today":
        date_range['start_date'] = datetime.today().date()
        date_range['end_date'] = datetime.today().date()
    elif title == "yesterday":
        date_range['start_date'] = datetime.today().date() - timedelta(days=1)
        date_range['end_date'] = datetime.today().date() - timedelta(days=1)
    elif title == "tomorrow":
        date_range['start_date'] = datetime.today().date() + timedelta(days=1)
        date_range['end_date'] = datetime.today().date() + timedelta(days=1)
    elif title == "this_week":
        date_range['start_date'] = datetime.today().date() - timedelta(days=datetime.today().weekday())
        date_range['end_date'] = date_range['start_date'] + timedelta(days=6)
    elif title == "this_month":
        date_range['start_date'] = datetime.today().date().replace(day=1)
        date_range['end_date'] = datetime.today().date() + relativedelta(day=31)
    
    date_range['start_date'] = str(date_range['start_date']) + " 00:00:00"
    date_range['end_date'] = str(date_range['end_date']) + " 23:59:59"
    return date_range




def create_google_calendar_event(data):
    print("===Google start===")
    from google.oauth2.credentials import Credentials
    user_credentials = Credentials.from_authorized_user_file('google_creds/token.json')
    print("User credential found")
    from googleapiclient.discovery import build
    
    service = build('calendar', 'v3', credentials=user_credentials)
    
    print("Service created")
    start_str = data.get("start_date")
    end_str = data.get("end_date")

    if not start_str or not end_str:
        raise ValueError("Start and end dates must not be empty.")
    print("Date all good")
    try:
        # Accepting formats like "2025-04-25T12:34:00" or "2025-04-25 12:34:00"
        start_dt = datetime.fromisoformat(start_str.replace(" ", "T"))
        end_dt = datetime.fromisoformat(end_str.replace(" ", "T"))
    except ValueError as e:
        print("Value Error 1  ", str(e))
        raise ValueError(f"Invalid date format: {e}")

    if start_dt >= end_dt:
        print("End time must be after start time.")
        raise ValueError("End time must be after start time.")

    print("Start Date and end ISsues pass ")

    event = {
        'summary': data.get("summary"),
        'location': data.get("location"),
        'description': data.get("description"),
        'start': {
            'dateTime': start_dt.isoformat(),
            'timeZone': 'Asia/Kolkata',
        },
        'end': {
            'dateTime': end_dt.isoformat(),
            'timeZone': 'Asia/Kolkata',
        },
        'attendees': data.get('attendees', []),
        'reminders': {
            'useDefault': False,
            'overrides': [
                {'method': 'popup', 'minutes': 30},
            ],
        },
    }

    print("Google Event Payload ", event)

    try:
        created_event = service.events().insert(
            calendarId='primary',
            body=event,
            sendUpdates='all'
        ).execute()
        print("Event created:",created_event, created_event.get('htmlLink'))
        return created_event
    except Exception as e:
        print("Error creating event:", e)


def delete_google_calendar_event(event_id):
    from google.oauth2.credentials import Credentials
    user_credentials = Credentials.from_authorized_user_file('google_creds/token.json')
    from googleapiclient.discovery import build
    
    service = build('calendar', 'v3', credentials=user_credentials)
    
    kwargs = {
        'calendarId': 'primary',
        'eventId': event_id,
        'sendNotifications': False
    }
    request = service.events().delete(**kwargs)
    resp = request.execute()
    return resp
