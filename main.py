import pandas as pd
import sys
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import json
import seaborn as sns
import matplotlib.pyplot as plt
import textwrap
import isodate

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
            if user_option in ['4', '5', '6']:
                while True:
                    num = input('\nHow many videos of the recent uploads would you like visualized for the trend? Pick a number between 1 - 50. \n')
                    if num.isdigit() and int(num) > 0 and int(num) < 51:
                        return int(user_option), int(num)
                    else:
                        print("Invalid input. Please enter a positive integer.")
            return int(user_option), None
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

    df = pd.DataFrame(requested_data)
    df.index += 1
    return df

def retrieve_video_ids(youtube, id, num_vids):
    list_ids = []
    next_page_token = None

    while len(list_ids) < num_vids:
        request = youtube.playlistItems().list(
            part="snippet, contentDetails",
            playlistId=id,
            maxResults=50,  # Fetch up to 50 items per request
            pageToken=next_page_token
        )
        response = request.execute()

        for item in response['items']:
            video_id = item['contentDetails']['videoId']

            # Get video details to check the duration
            video_request = youtube.videos().list(
                part="contentDetails",
                id=video_id
            )
            video_response = video_request.execute()
            duration = video_response['items'][0]['contentDetails']['duration']
            duration_seconds = isodate.parse_duration(duration).total_seconds()

            if duration_seconds > 60:
                list_ids.append(video_id)
                if len(list_ids) == num_vids:
                    break

        next_page_token = response.get('nextPageToken')

        if not next_page_token:
            break

    return list_ids

def get_trend_stats(youtube, usernames, option, retrieved, ids, list_videoids, num_vids):
    # IF FIRST ITERATION, AND DATA HAS NEVER BEEN CALCULATED, STORE IN DICTIONARY
    if not retrieved:
        for username in usernames:
            request = youtube.channels().list(
                part="contentDetails",
                forUsername=username
            )
            response = request.execute() 

            for item in response.get('items', []):
                x = item['contentDetails']['relatedPlaylists']['uploads']
                ids.append(x)

        for string_id in ids:
            videos_list = retrieve_video_ids(youtube, string_id, num_vids)
            list_videoids[string_id] = videos_list
    
    trend_data = []

    for id in ids:
        request = youtube.videos().list(
            part="snippet,statistics",
            id=','.join(list_videoids[id][0:num_vids])
        )
        response = request.execute()

        for vid in response['items']:
            if option == 4:
                data = {
                    'Channel': vid['snippet']['channelTitle'],
                    'Video ID': vid['id'],
                    'Video Title': vid['snippet']['title'],
                    'View Count': vid['statistics']['viewCount']
                }
            elif option == 5:
                data = {
                    'Channel': vid['snippet']['channelTitle'],
                    'Video ID': vid['id'],
                    'Video Title': vid['snippet']['title'],
                    'Like Count': vid['statistics']['likeCount']
                }
            elif option == 6:
                data = {
                    'Channel': vid['snippet']['channelTitle'],
                    'Video ID': vid['id'],
                    'Video Title': vid['snippet']['title'],
                    'Comment Count': vid['statistics']['commentCount']
                }
            trend_data.append(data)
    
    df = pd.DataFrame(trend_data)
    df.index += 1
    return df

def trend_data_preprocessing(dfs, option):
    if option == 4:
        dfs['View Count'] = dfs['View Count'].apply(pd.to_numeric, errors='coerce')
    elif option == 5:
        dfs['Like Count'] = dfs['Like Count'].apply(pd.to_numeric, errors='coerce')
    elif option == 6:
        dfs['Comment Count'] = dfs['Comment Count'].apply(pd.to_numeric, errors='coerce')
    return dfs

def main():
    # MAIN CODE
    api_key = input("----------Welcome----------\nPlease enter your API Key\n")
    if not check_api_key(api_key):
        print("Invalid API Key. Exiting program.")
        sys.exit(1)

    api_service_name = "youtube"
    api_version = "v3"
    youtube = build(api_service_name, api_version, developerKey=api_key)

    username_list = input("\nPlease enter the usernames of the channels you would like to analyze, separated by a single space between each one.MAKE SURE THE USERNAMES ARE"
                          " SPELLED CORRECTLY.\nThere are over 114 million youtube channels, so this program will not be able to differentiate between whether the user inputted channels have a typo or are valid usernames:\n")

    channels = username_list.split()

    if len(channels) < 1:
        print("No usernames were provided. Please provide a list of valid usernames separated by a single space.\n")
        sys.exit(1)

    playlist_ids = []
    retrieved_playlist_ids = False
    playlist_to_videoids = {}

    while True:
        user_option, numvids = get_user_option()
        if user_option == 7:
            break

        if user_option == 1:
            channel_analytics = get_simple_stats(youtube, channels, 1)
            channel_analytics['Total View Count'] = channel_analytics['Total View Count'].apply(pd.to_numeric, errors='coerce')
            channel_analytics = channel_analytics.sort_values('Total View Count', ascending=False)
            for index, row in channel_analytics.iterrows():
                channel_name = row['Channel Name']
                plt.figure(figsize=(15, 10))
                ax = sns.barplot(x='Total View Count', y='Channel Name', data=channel_analytics)
                ax.set_title(f'Channels by Total View Count - {channel_name}')
                ax.set_xlabel('Total View Count')
                ax.set_ylabel('Channel Name')
                plt.show()

        elif user_option == 2:
            channel_analytics = get_simple_stats(youtube, channels, 2)
            channel_analytics['Subscriber Count'] = channel_analytics['Subscriber Count'].apply(pd.to_numeric, errors='coerce')
            channel_analytics = channel_analytics.sort_values('Subscriber Count', ascending=False)
            for index, row in channel_analytics.iterrows():
                channel_name = row['Channel Name']
                plt.figure(figsize=(15, 10))
                ax = sns.barplot(x='Subscriber Count', y='Channel Name', data=channel_analytics)
                ax.set_title(f'Channels by Subscriber Count - {channel_name}')
                ax.set_xlabel('Subscriber Count')
                ax.set_ylabel('Channel Name')
                plt.show()

        elif user_option == 3:
            channel_analytics = get_simple_stats(youtube, channels, 3)
            channel_analytics['Video Upload Count'] = channel_analytics['Video Upload Count'].apply(pd.to_numeric, errors='coerce')
            channel_analytics = channel_analytics.sort_values('Video Upload Count', ascending=False)
            for index, row in channel_analytics.iterrows():
                channel_name = row['Channel Name']
                plt.figure(figsize=(15, 10))
                ax = sns.barplot(x='Video Upload Count', y='Channel Name', data=channel_analytics)
                ax.set_title(f'Channels by Video Upload Count - {channel_name}')
                ax.set_xlabel('Video Upload Count')
                ax.set_ylabel('Channel Name')
                plt.show()

        elif user_option == 4:
            trend_data = get_trend_stats(youtube, channels, user_option, retrieved_playlist_ids, playlist_ids, playlist_to_videoids, numvids)
            retrieved_playlist_ids = True
            trend_data['View Count'] = trend_data['View Count'].apply(pd.to_numeric, errors='coerce')

            for i in range(0, len(trend_data), numvids):
                # Ensure the slice doesn't go beyond the length of the DataFrame
                slice_end = min(i + numvids, len(trend_data))
                sliced_data = trend_data[i:slice_end]
                channel_name = sliced_data.iloc[0]['Channel']  # Assuming 'Channel' column contains channel names

                plt.figure(figsize=(15, 10))
                ax = sns.barplot(x='Video Title', y='View Count', data=sliced_data)
                ax.set_title(f'Latest Videos by View Count - {channel_name}')
                ax.set_xlabel('Video Title')
                ax.set_ylabel('View Count')

                plt.xticks(rotation=0, ha='right', fontsize=10)
                # Wrap long titles
                ax.set_xticklabels([textwrap.fill(label.get_text(), width=20) for label in ax.get_xticklabels()])
                
                plt.tight_layout() 
                plt.show()

        elif user_option == 5:
            trend_data = get_trend_stats(youtube, channels, user_option, retrieved_playlist_ids, playlist_ids, playlist_to_videoids, numvids)
            retrieved_playlist_ids = True
            trend_data['Like Count'] = trend_data['Like Count'].apply(pd.to_numeric, errors='coerce')

            for i in range(0, len(trend_data), numvids):
                # Ensure the slice doesn't go beyond the length of the DataFrame
                slice_end = min(i + numvids, len(trend_data))
                sliced_data = trend_data[i:slice_end]
                channel_name = sliced_data.iloc[0]['Channel']  # Assuming 'Channel' column contains channel names

                plt.figure(figsize=(15, 10))
                ax = sns.barplot(x='Video Title', y='Like Count', data=sliced_data)
                ax.set_title(f'Latest Videos by Like Count - {channel_name}')
                ax.set_xlabel('Video Title')
                ax.set_ylabel('Like Count')

                plt.xticks(rotation=0, ha='right', fontsize=10)
                # Wrap long titles
                ax.set_xticklabels([textwrap.fill(label.get_text(), width=20) for label in ax.get_xticklabels()])
                plt.show()

        else:
            trend_data = get_trend_stats(youtube, channels, user_option, retrieved_playlist_ids, playlist_ids, playlist_to_videoids, numvids)
            retrieved_playlist_ids = True
            trend_data['Comment Count'] = trend_data['Comment Count'].apply(pd.to_numeric, errors='coerce')

            for i in range(0, len(trend_data), numvids):
                # Ensure the slice doesn't go beyond the length of the DataFrame
                slice_end = min(i + numvids, len(trend_data))
                sliced_data = trend_data[i:slice_end]
                channel_name = sliced_data.iloc[0]['Channel']  # Assuming 'Channel' column contains channel names

                plt.figure(figsize=(15, 10))
                ax = sns.barplot(x='Video Title', y='Comment Count', data=sliced_data)
                ax.set_title(f'Latest Videos by Comment Count - {channel_name}')
                ax.set_xlabel('Video Title')
                ax.set_ylabel('Comment Count')

                plt.xticks(rotation=0, ha='right', fontsize=10)
                # Wrap long titles
                ax.set_xticklabels([textwrap.fill(label.get_text(), width=20) for label in ax.get_xticklabels()])
                plt.show()

    print("\n----------Data Visualization Complete!----------\n")

if __name__ == "__main__":
    main()
