import os
import json
import datetime

def get_all_emails(email_folder):
    email_objs = []
    for root, dirs, filenames in os.walk(email_folder):
        for filename in filenames:
            filepath = os.path.join(root, filename)
            with open(filepath) as f:
                email_obj = json.load(f)
                email_objs.append(email_obj)
    return email_objs
    

# "timestamp": "13-Aug-2021 22:40:52.603733", "ip": "112.200.198.49"
def get_valids(valid_folder):
    valid_objs = []
    for root, dirs, filenames in os.walk(valid_folder):
        for filename in filenames:
            filepath = os.path.join(root, filename)
            with open(filepath) as f:
                valid_obj = json.load(f)
                small_obj = {
                    "timestamp": datetime.datetime.strptime(valid_obj["timestamp"], "%d-%b-%Y %H:%M:%S.%f"),
                    "ip": valid_obj["ip"]
                }
                valid_objs.append(small_obj)
    return valid_objs


email_folder = "emails"
valid_folder = "valid_study"

email_objs = get_all_emails(email_folder)
valid_objs = get_valids(valid_folder)
# [print(obj["email"] ) for obj in email_objs]

valid_objs.sort(key=lambda x: x["timestamp"])
# [print(obj["ip"] ) for obj in valid_objs]


emails = []
for obj in valid_objs[:100]:
    for i, email_obj in enumerate(email_objs):
        if obj["ip"] == email_obj["ip"]:
            break
    emails.append(email_obj["email"])
    email_objs.pop(i)

[print(email) for email in emails]

