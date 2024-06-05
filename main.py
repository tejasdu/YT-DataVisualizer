import pandas as pd
import sys
from googleapiclient.discovery import build
import json

def get_user_option():
    while True:
        user_option = input("\nSelect the analytics you would like visualized by entering 1, 2 or 3:\n"
                            "   1) Total View Count\n"
                            "   2) Subscriber Count\n"
                            "   3) Video Upload Count\n") 
        if user_option in ['1', '2', '3']:
            return int(user_option)
        else:
            print("Invalid selection. Please enter the option 1, 2 or 3\n")

def get_stats(youtube, usernames, option): 
    requested_data = []

    for username in usernames:
        request = youtube.channels().list(
            part="snippet,contentDetails,statistics",
            forUsername=username
        )
        response = request.execute()

        for item in response.get('items', []):
            if option == 1:
                data = {
                    'Channel Name': item['snippet']['title'],
                    'Total View Count': item['statistics']['viewCount']
                }
            elif option == 2:
                data = {
                    'Channel Name': item['snippet']['title'],
                    'Subscriber Count': item['statistics']['subscriberCount']
                }
            elif option == 3:
                data = {
                    'Channel Name': item['snippet']['title'],
                    'Video Upload Count': item['statistics']['videoCount']
                }

            requested_data.append(data)

    return pd.DataFrame(requested_data)

# In order to run the program on your own device, follow the README instructions and create your own API KEY in order to access the information 
api_key = input("Please enter your API Key\n")
# AIzaSyDKYxmMDtjfhQQaEryWuAShYN9VUPXWY9k

api_service_name = "youtube"
api_version = "v3"
# Get credentials and create an API client
youtube = build(api_service_name, api_version, developerKey=api_key)

username_list = input("\nPlease enter the usernames of the channels you would like to analyze, seperated by a single space between each one.\nMAKE SURE THE USERNAMES ARE"
                      " SPELLED CORRECTLY.\nThere are over 114 million youtube channels, so this program will not be able to diffrentiate between whether the user inputed channels have a typo or are valid usernames:\n")

channels = username_list.split()

if len(channels) < 1:
    print("No usernames were provided. Please provide a list valid usernames seperated by a single space.\n")
    sys.exit(1)

user_option = get_user_option()
channel_analytics = get_stats(youtube,channels,user_option)
