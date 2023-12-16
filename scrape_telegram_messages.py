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
            data = { "group" : chat, "sender" : message.sender_id, "text" : message.text, "date" : message.date}
            temp_df = pd.DataFrame(data, index=[0])

            df = pd.concat([temp_df, df.loc[:]]).reset_index(drop=True)

df['date'] = df['date'].dt.tz_localize(None)

df.to_excel(os.path.join(os.getcwd(), "data_{}.xlsx".format(datetime.date.today())), index=False) # file name is the date of retrieval
