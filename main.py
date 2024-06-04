import requests
import pandas
import sys
from googleapiclient.discovery import build


# In order to run the program on your own device, follow the README instructions and create your own API KEY in order to access the information 
api_key = input("Please Enter your API Key\n")
# AIzaSyDKYxmMDtjfhQQaEryWuAShYN9VUPXWY9k

api_service_name = "youtube"
api_version = "v3"
# Get credentials and create an API client
youtube = build(api_service_name, api_version, developerKey=api_key)

username_list = input("Please enter the usernames of the channels you would like to analyze, seperated by a single space between each one.\nMAKE SURE THE USERNAMES ARE"
                      " SPELLED CORRECTLY. There are over 114 million youtube channels, so this program will not be able to diffrentiate between whether there the user inputed channels have a typo or are valid names:\n")
channels = username_list.split()


if len(channels) < 1:
    print("No usernames were provided. Please provide a list valid usernames seperated by a single space.\n")
    sys.exit(1)

responses = []

for channel in channels:
    request = youtube.channels().list(
        part="snippet,contentDetails,statistics",
        forUsername=channel
    )

    response = request.execute()
    responses.append(response)

for i, response in enumerate(responses):
    print(f"Extracting data for the channel: {channels[i]}: ")
    print(response)
    print()


