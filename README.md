--------------------------------------------------------------------------------
YOUTUBE CHANNEL ANALYTICS DATA VISUALIZER: 
A tool to visualize and analyze key metrics of YouTube channels.
--------------------------------------------------------------------------------

Youtube Studio has channel statistics and visualisations for ones own channel, but it severely limited in that regard. By supporting the comparison of multiple channels, this program alleviates that setback and allows for the user to perform their own data analytic studies on channels they wish to compare. This opens the door for users to perform and obtain complex channel feedback, and information on trends and community engagement, making this an effective tool unlike standard channel statistics provided by Youtube.

Welcome to the YouTube Channel Analytics Visualizer! This tool provides a comprehensive way to analyze and visualize the key metrics of YouTube channels. Users can gain insights into various statistics like total view counts, subscriber counts, video upload counts, and trends in view, like, and comment counts for the most recent uploads. This project leverages the Google for Developers tool, "YouTube Data API" to fetch the required data and uses important packages such as numpy, pandas, seaborn and matplotlib for creating the visualizations. 

----------------------------------------
INSTALLATION INSTRUCTIONS FOR USERS
----------------------------------------
Clone the Repository:
    git clone https://github.com/yourusername/youtube-channel-analytics-visualizer.git
    cd youtube-channel-analytics-visualizer
  
Install the Required Packages:
    pip install -r requirements.txt

Run the Application:
    python main.py

Creating your own API Key
    This program requires you to use your own API Key in order to access YT's channel data. Follow these steps to get your API Key
    
    - Step 1: Create a Google Cloud Project
        Visit the Google Cloud Console.
        Sign in with your Google account.
        Create a new project:
        Click on the project dropdown at the top of the page.
        Click on "New Project".
        Enter a name for your project (e.g., "YouTube Data Project").
        Click "Create".
  
    - Step 2: Enable the YouTube Data API
        Navigate to the API Library:
        In the left sidebar, go to "APIs & Services" > "Library".
        Search for "YouTube Data API v3".
        Enable the API:
        Click on "YouTube Data API v3" from the search results.
        Click the "Enable" button.
        
    - Step 3: Create API Credentials
        Go to the Credentials page:
        In the left sidebar, go to "APIs & Services" > "Credentials".
        Create new credentials:
        Click the "Create Credentials" button at the top.
        Select "API key" from the dropdown menu.
        API key created:
        Your new API key will be displayed.
        Click "Copy" to copy your API key. You will use this key in your YouTube Channel Analytics Visualizer.
        
    - Step 4: Restrict Your API Key (Optional but Recommended)
      Click on the API key name in the Credentials page to open its settings.
      Restrict the key:
      Under "API restrictions", select "Restrict key".
      Select "YouTube Data API v3" from the list.
      Click "Save" to apply the restrictions.
----------------------------------------
KNOWN ISSUES
----------------------------------------
    - API Key Invalidity: If the provided API key is invalid, the program will exit. Ensure you have a valid YouTube Data API key.
    - Typo in Usernames: The program cannot differentiate between typos and invalid usernames due to the vast number of YouTube channels.
    - Long Video Titles: Long video titles may still cause some overlap in visualizations despite the text wrapping.
    
If you encounter any other issues, please report them via GitHub issues.

---------------------------------------------------------------------------------
Thank you for using and contributing to the YouTube Channel Analytics Visualizer!
---------------------------------------------------------------------------------
