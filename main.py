import pandas as pd
import sys
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import json

def check_api_key(api_key):
    try:
        youtube = build('youtube', 'v3', developerKey=api_key)
        request = youtube.channels().list(part='snippet', forUsername='Google')
        response = request.execute()
        return True
    except HttpError as e:
        error_content = json.loads(e.content.decode('utf-8'))
        error_reason = error_content['error']['errors'][0]['reason']
        if error_reason == 'keyInvalid':
            return False
        else:
            raise

def get_user_option():
    while True:
        user_option = input("\nSelect the analytics you would like visualized by entering a number from 1-7 corresponding to the options below:\n"
                            "   1) Total View Count\n"
                            "   2) Subscriber Count\n"
                            "   3) Video Upload Count\n"
                            "   4) View Count Trend\n"
                            "   5) Like Count Trend\n"
                            "   6) Comment Count Trend\n"
                            "   7) QUIT\n") 
        if user_option in ['1', '2', '3', '4', '5', '6', '7']:
            return int(user_option)
        else:
            print("Invalid selection. Please enter a number 1-7 corresponding to the options displayed. \n")

def get_simple_stats(youtube, usernames, option): 
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
            else:
                data = {
                    'Channel Name': item['snippet']['title'],
                    'Video Upload Count': item['statistics']['videoCount']
                }
            requested_data.append(data)
            
    return pd.DataFrame(requested_data)

def get_trend_stats(youtube, usernames, option, retrieved, ids):
    requested_data = []

    #GET 'UPLOADS' PLAYLIST ID TO LOOK THROUGH 
    if retrieved == False:
        for username in usernames:
            request = youtube.channels().list(
                part="contentDetails",
                forUsername=username
            )
            response = request.execute() 

            for item in response.get('items', []):
                x = item['contentDetails']['relatedPlaylists']['uploads']
                ids.append(x)
    
    #IF PLAYLIST IDS WERE ALREADY STORED FROM A PREVIOUS REQUEST
    else:
        if option == 4:
            print("TBD")
        elif option == 5:
            print("TBD") 
        else:
            print("TBD")

def main():
    #MAIN CODE
    api_key = input("Please enter your API Key\n")
    if not check_api_key(api_key):
        print("Invalid API Key. Exiting program.")
        sys.exit(1)

    api_service_name = "youtube"
    api_version = "v3"
    youtube = build(api_service_name, api_version, developerKey=api_key)

    username_list = input("\nPlease enter the usernames of the channels you would like to analyze, separated by a single space between each one.\nMAKE SURE THE USERNAMES ARE"
                          " SPELLED CORRECTLY.\nThere are over 114 million youtube channels, so this program will not be able to differentiate between whether the user inputted channels have a typo or are valid usernames:\n")

    channels = username_list.split()

    if len(channels) < 1:
        print("No usernames were provided. Please provide a list of valid usernames separated by a single space.\n")
        sys.exit(1)

    playlist_ids = []
    retrived_playlist_ids = False

    while True:
        user_option = get_user_option()
        if user_option == 7:
            break

        if user_option in [1, 2, 3]:
            channel_analytics = get_simple_stats(youtube, channels, user_option)
            print(channel_analytics)
        else:
            trend_data = get_trend_stats(youtube, channels, user_option,retrived_playlist_ids, playlist_ids)
            retrived_playlist_ids = True
    
    print(playlist_ids)
    print("\n----------Data Visualization Complete!----------\n")

if __name__ == "__main__":
    main()
