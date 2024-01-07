from telethon.sync import TelegramClient
import datetime
import pandas as pd
import os
import configparser

# Read Telegram API credentials from a configuration file
config = configparser.ConfigParser()
config.read("telethon.config")
api_id = config["telethon_credentials"]["api_id"]
api_hash = config["telethon_credentials"]["api_hash"]

# Specify the list of chats to scrape
chats = ['sethisfychat']

# Create an empty DataFrame with column headers to store the scraped data
df = pd.DataFrame(columns=["message_id", "group", "sender", "text", "date", "direct_reply_to", "original_message_id"])

# Loop through each specified chat
for chat in chats:
    # Initialize a TelegramClient with the specified API credentials
    with TelegramClient('messages', api_id, api_hash) as client:
        # Iterate over messages in the chat, starting from 6 days ago to the current date
        for message in client.iter_messages(chat, offset_date=datetime.date.today() - datetime.timedelta(days=6), reverse=True): # right now it's set to get chat history from 6 days ago to current date
            
            # Remove newline characters from the message text to help import into postgreSQL
            cleaned_message_text = message.message.replace('\n', ' ')

            # Print the message in the terminal of the developer for debugging purposes
            # print(message)
            print(cleaned_message_text)

            # Create a dictionary to store specific message fields that we want to extract
            data = { "message_id" : message.id, "group" : chat, "sender" : message.sender_id, "text" : cleaned_message_text, "date" : message.date, "direct_reply_to" : message.reply_to_msg_id, "original_message_id": None }
            
            # Extract information about the direct reply chain to find the original_message_id at the top of the reply chain for each message
            direct_reply_to = message.reply_to_msg_id
            while direct_reply_to:
                original_message_id = df.loc[df['message_id'] == direct_reply_to, 'message_id'].values
                if original_message_id.size > 0:
                    data["original_message_id"] = original_message_id[0]
                    direct_reply_to = df.loc[df['message_id'] == direct_reply_to, 'direct_reply_to'].values[0]
                else:
                    break
            
            # Create a temporary DataFrame to store the message information
            temp_df = pd.DataFrame(data, index=[0])

            # Concatenate the temporary DataFrame with the main DataFrame
            df = pd.concat([temp_df, df.loc[:]]).reset_index(drop=True)

# Remove timezone information from the 'date' column
df['date'] = df['date'].dt.tz_localize(None)

# Save the DataFrame to an Excel file with the current date set as the filename
df.to_excel(os.path.join(os.getcwd(), "data_{}.xlsx".format(datetime.date.today())), index=False) # file name is the date of retrieval
