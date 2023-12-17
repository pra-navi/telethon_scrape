from telethon.sync import TelegramClient
import datetime
import pandas as pd
import os

import configparser
config = configparser.ConfigParser()
config.read("telethon.config")

api_id = config["telethon_credentials"]["api_id"]
api_hash = config["telethon_credentials"]["api_hash"]

chats = ['sethisfychat'] # list of chats to scrape

df = pd.DataFrame()

for chat in chats:
    with TelegramClient('messages', api_id, api_hash) as client:
        for message in client.iter_messages(chat, offset_date=datetime.date.today() - datetime.timedelta(days=6), reverse=True): # right now it's set to get chat history from 6 days ago to current date
            print(message)
            data = { "message_id" : message.id, "group" : chat, "sender" : message.sender_id, "text" : message.text, "date" : message.date, "direct_reply_to" : message.reply_to_msg_id, "original_message_id": None }
            
            direct_reply_to = message.reply_to_msg_id
            while direct_reply_to:
                original_message_id = df.loc[df['message_id'] == direct_reply_to, 'message_id'].values
                if original_message_id:
                    data["original_message_id"] = original_message_id[0]
                    direct_reply_to = df.loc[df['message_id'] == direct_reply_to, 'direct_reply_to'].values[0]
                else:
                    break
            
            temp_df = pd.DataFrame(data, index=[0])

            df = pd.concat([temp_df, df.loc[:]]).reset_index(drop=True)

df['date'] = df['date'].dt.tz_localize(None)

df.to_excel(os.path.join(os.getcwd(), "data_{}.xlsx".format(datetime.date.today())), index=False) # file name is the date of retrieval
