import pandas as pd
import sys
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import json
import seaborn as sns
import matplotlib.pyplot as plt
import isodate
import textwrap

class YouTubeAnalytics:
    def __init__(self, api_key):
        self.api_key = api_key
        self.youtube = build('youtube', 'v3', developerKey=self.api_key)
        self.playlist_ids = []
        self.retrieved_playlist_ids = False
        self.playlist_to_videoids = {}

    def check_api_key(self):
        try:
            request = self.youtube.channels().list(part='snippet', forUsername='Google')
            response = request.execute()
            return True
        except HttpError as e:
            error_content = json.loads(e.content.decode('utf-8'))
            error_reason = error_content['error']['errors'][0]['reason']
            if error_reason == 'keyInvalid':
                return False
            else:
                raise

    def get_user_option(self):
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
                        if num.isdigit() and 1 <= int(num) <= 50:
                            return int(user_option), int(num)
                        else:
                            print("Invalid input. Please enter a positive integer.")
                return int(user_option), None
            else:
                print("Invalid selection. Please enter a number 1-7 corresponding to the options displayed. \n")

    def get_simple_stats(self, usernames, option):
        option_key_map = {
            1: 'viewCount',
            2: 'subscriberCount',
            3: 'videoCount'
        }
        
        option_label_map = {
            1: 'Total View Count',
            2: 'Subscriber Count',
            3: 'Video Upload Count'
        }
        
        requested_data = []

        for username in usernames:
            request = self.youtube.channels().list(
                part="snippet,contentDetails,statistics",
                forUsername=username
            )
            response = request.execute()

            for item in response.get('items', []):
                data = {
                    'Channel Name': item['snippet']['title'],
                    option_label_map[option]: item['statistics'][option_key_map[option]]
                }
                requested_data.append(data)

        df = pd.DataFrame(requested_data)
        df.index += 1
        return df

    def retrieve_video_ids(self, id, num_vids):
        list_ids = []
        next_page_token = None

        while len(list_ids) < num_vids:
            request = self.youtube.playlistItems().list(
                part="snippet, contentDetails",
                playlistId=id,
                maxResults=50,
                pageToken=next_page_token
            )
            response = request.execute()

            for item in response['items']:
                video_id = item['contentDetails']['videoId']

                video_request = self.youtube.videos().list(
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

    def get_trend_stats(self, usernames, option, num_vids):
        option_key_map = {
            4: 'viewCount',
            5: 'likeCount',
            6: 'commentCount'
        }
        option_label_map = {
            4: 'View Count',
            5: 'Like Count',
            6: 'Comment Count'
        }

        if not self.retrieved_playlist_ids:
            for username in usernames:
                request = self.youtube.channels().list(
                    part="contentDetails",
                    forUsername=username
                )
                response = request.execute()

                for item in response.get('items', []):
                    x = item['contentDetails']['relatedPlaylists']['uploads']
                    self.playlist_ids.append(x)

            for string_id in self.playlist_ids:
                videos_list = self.retrieve_video_ids(string_id, num_vids)
                self.playlist_to_videoids[string_id] = videos_list

        trend_data = []

        for id in self.playlist_ids:
            request = self.youtube.videos().list(
                part="snippet,statistics",
                id=','.join(self.playlist_to_videoids[id][0:num_vids])
            )
            response = request.execute()

            for vid in response['items']:
                data = {
                    'Channel': vid['snippet']['channelTitle'],
                    'Video ID': vid['id'],
                    'Video Title': vid['snippet']['title'],
                    option_label_map[option]: vid['statistics'][option_key_map[option]]
                }
                trend_data.append(data)

        df = pd.DataFrame(trend_data)
        df.index += 1
        return df

    def trend_data_preprocessing(self, dfs, option):
        if option == 4:
            dfs['View Count'] = dfs['View Count'].apply(pd.to_numeric, errors='coerce')
        elif option == 5:
            dfs['Like Count'] = dfs['Like Count'].apply(pd.to_numeric, errors='coerce')
        elif option == 6:
            dfs['Comment Count'] = dfs['Comment Count'].apply(pd.to_numeric, errors='coerce')
        return dfs

    def plot_channel_analytics(self, channel_analytics, metric, title):
        plt.figure(figsize=(15, 10))
        ax = sns.barplot(x=metric, y='Channel Name', data=channel_analytics)
        ax.set_title(f'Channels by {title}')
        ax.set_xlabel(title)
        ax.set_ylabel('Channel Name')
        plt.show()

    def plot_trend_data(self, trend_data, metric, numvids):
        for i in range(0, len(trend_data), numvids):
            slice_end = min(i + numvids, len(trend_data))
            sliced_data = trend_data[i:slice_end]
            channel_name = sliced_data.iloc[0]['Channel']

            plt.figure(figsize=(20, 10))  # Increase figure width
            ax = sns.barplot(x='Video Title', y=metric, data=sliced_data)
            ax.set_title(f'Latest Videos by {metric} - {channel_name}')
            ax.set_xlabel('Video Title')
            ax.set_ylabel(metric)

            plt.xticks(rotation=45, ha='right', fontsize=10)
            ax.set_xticklabels([textwrap.fill(label.get_text(), width=30) for label in ax.get_xticklabels()])

            plt.tight_layout()  # Ensure everything fits without overlapping

            plt.show()

    def main(self):
        if not self.check_api_key():
            print("Invalid API Key. Exiting program.")
            sys.exit(1)

        username_list = input("\nPlease enter the usernames of the channels you would like to analyze, separated by a single space between each one. MAKE SURE THE USERNAMES ARE"
                              " SPELLED CORRECTLY.\nThere are over 114 million youtube channels, so this program will not be able to differentiate between whether the user inputted channels have a typo or are valid usernames:\n")

        channels = username_list.split()

        if len(channels) < 1:
            print("No usernames were provided. Please provide a list of valid usernames separated by a single space.\n")
            sys.exit(1)

        while True:
            user_option, numvids = self.get_user_option()
            if user_option == 7:
                break

            if user_option == 1:
                channel_analytics = self.get_simple_stats(channels, 1)
                channel_analytics['Total View Count'] = channel_analytics['Total View Count'].apply(pd.to_numeric, errors='coerce')
                channel_analytics = channel_analytics.sort_values('Total View Count', ascending=False)
                self.plot_channel_analytics(channel_analytics, 'Total View Count', 'Total View Count')

            elif user_option == 2:
                channel_analytics = self.get_simple_stats(channels, 2)
                channel_analytics['Subscriber Count'] = channel_analytics['Subscriber Count'].apply(pd.to_numeric, errors='coerce')
                channel_analytics = channel_analytics.sort_values('Subscriber Count', ascending=False)
                self.plot_channel_analytics(channel_analytics, 'Subscriber Count', 'Subscriber Count')

            elif user_option == 3:
                channel_analytics = self.get_simple_stats(channels, 3)
                channel_analytics['Video Upload Count'] = channel_analytics['Video Upload Count'].apply(pd.to_numeric, errors='coerce')
                channel_analytics = channel_analytics.sort_values('Video Upload Count', ascending=False)
                self.plot_channel_analytics(channel_analytics, 'Video Upload Count', 'Video Upload Count')

            elif user_option in [4, 5, 6]:
                trend_data = self.get_trend_stats(channels, user_option, numvids)
                trend_data = self.trend_data_preprocessing(trend_data, user_option)
                self.retrieved_playlist_ids = True

                metric = 'View Count' if user_option == 4 else 'Like Count' if user_option == 5 else 'Comment Count'
                self.plot_trend_data(trend_data, metric, numvids)

        print("\n----------Data Visualization Complete!----------\n")


if __name__ == "__main__":
    api_key = input("----------Welcome----------\nPlease enter your API Key\n")
    visualizer = YouTubeAnalytics(api_key)
    visualizer.main()
