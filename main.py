TOKEN = ""  # Authentication token. Do not share this.WhitelistedServers = ["796334983542341632", "911382562000211999", "698304586481533030", "924497342156111912", "984582850588340264", "740977707629805669", "1011606221914128505", "877096010969645086"]  # List of server IDs to ignore.
WhitelistedUsers = [""]  # List of user IDs to ignore
WhitelistedFriendships = [""]
YourUserID = ""

# ----------- #

import requests as req
import websocket
import json
import random
import time

# ----------- #

BaseDeleteDelay = 2600


# ----------- #

def generate_headers() -> dict:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) discord/1.0.9007 Chrome/91.0.4472.164 Electron/13.6.6 Safari/537.36",
        "Accept-Language": "en-GB",
        "locale": "en-GB",
        "X-Debug-Options": "bugReporterEnabled",
        "X-Discord-Locale": "en-GB",
        "X-Super-Properties": "eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiRGlzY29yZCBDbGllbnQiLCJyZWxlYXNlX2NoYW5uZWwiOiJzdGFibGUiLCJjbGllbnRfdmVyc2lvbiI6IjEuMC45MDA3Iiwib3NfdmVyc2lvbiI6IjEwLjAuMjI2MjEiLCJvc19hcmNoIjoieDY0Iiwic3lzdGVtX2xvY2FsZSI6ImVuLUdCIiwiY2xpZW50X2J1aWxkX251bWJlciI6MTU2MDgwLCJjbGllbnRfZXZlbnRfc291cmNlIjpudWxsfQ==",
        "Authorization": f"{TOKEN}",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "Host": "discord.com"
    }

    return headers


def generate_random_time() -> int:
    offset = random.randint(100, 500)
    final_time = BaseDeleteDelay + offset

    return final_time


def error_catcher(error: str):
    if error == "invalid_token":
        print("Invalid Token!")
    pass


def validate_token() -> bool:
    r = req.get("https://discord.com/api/v9/users/@me", headers=generate_headers())
    if r.status_code != 200:
        return False
    return True


def fetch_identify() -> str:
    socket = websocket.create_connection("wss://gateway.discord.gg/?encoding=json&v=9")
    print(socket.recv())
    data = "{\"op\":2,\"d\":{\"token\":\"" + TOKEN + "\",\"capabilities\":1021,\"properties\":{\"os\":\"Windows\"," \
                                                     "\"browser\":\"Chrome\",\"device\":\"\"," \
                                                     "\"system_locale\":\"en-GB\"," \
                                                     "\"browser_user_agent\":\"Mozilla/5.0 (Windows NT 10.0; Win64; " \
                                                     "x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 " \
                                                     "Safari/537.36\",\"browser_version\":\"106.0.0.0\"," \
                                                     "\"os_version\":\"10\",\"referrer\":\"https://www.bing.com/\"," \
                                                     "\"referring_domain\":\"www.bing.com\"," \
                                                     "\"search_engine\":\"bing\",\"referrer_current\":\"\"," \
                                                     "\"referring_domain_current\":\"\"," \
                                                     "\"release_channel\":\"stable\",\"client_build_number\":156080," \
                                                     "\"client_event_source\":null},\"presence\":{" \
                                                     "\"status\":\"online\",\"since\":0,\"activities\":[]," \
                                                     "\"afk\":false},\"compress\":false,\"client_state\":{" \
                                                     "\"guild_hashes\":{},\"highest_last_message_id\":\"0\"," \
                                                     "\"read_state_version\":0,\"user_guild_settings_version\":-1," \
                                                     "\"user_settings_version\":-1," \
                                                     "\"private_channels_version\":\"0\"}}} "
    print(data)
    socket.send(data)
    identify_data: str = socket.recv()
    data = identify_data.encode("ascii", "ignore").decode()
    socket.close()

    return data


def unfriend_leftovers():
    print("Deleting leftover friends")
    data = fetch_identify()
    identify_json = json.loads(data)
    for relationship in identify_json["d"]["relationships"]:
        user_id = str(relationship["user_id"])
        if user_id not in WhitelistedUsers:
            if user_id not in WhitelistedFriendships:
                r = req.delete(f"https://discord.com/api/v9/users/@me/relationships/{user_id}",
                               headers=generate_headers())
                if r.status_code == 204:
                    print(f"Deleted friendship with {user_id}")
                else:
                    print(f"Failed to delete friendship with {user_id} - Code: {r.status_code}")
                time.sleep(0.3)


def fetch_dms():
    data = fetch_identify()
    identify_json = json.loads(data)
    for dm in identify_json["d"]["private_channels"]:
        if dm["type"] == 1:
            try:
                user_id = str(dm["user_id"])
            except KeyError:
                user_id = str(dm["recipient_ids"][0])
            channel_id = str(dm["id"])
            print(f"User ID: {user_id}")
            print(f"Channel ID: {channel_id}")
            if user_id in WhitelistedUsers:
                continue
            else:
                if user_id not in WhitelistedUsers:
                    messages = fetch_all_messages(dm["id"])
                    wipe_dm(messages, user_id)


def wipe_dm(message_list, user_id):
    if not message_list:
        return
    try:
        current_channel = message_list[0]["channel_id"]
    except IndexError:
        return
    print(f"Current channel ID: {current_channel}")
    for message in message_list:
        if message["author"]["id"] == YourUserID:
            current_channel = message["channel_id"]
            message_id = message["id"]
            r = req.delete(f"https://discord.com/api/v9/channels/{current_channel}/messages/{message_id}",
                           headers=generate_headers())
            if r.status_code == 204:
                print(f"Successfully deleted message ID {message_id} - channel {current_channel}")
            else:
                print(f"Failed to delete message ID {message_id} - channel {current_channel} - Code: {r.status_code}")
            time.sleep(generate_random_time() / 1000)
    if user_id not in WhitelistedFriendships:
        r = req.delete(f"https://discord.com/api/v9/users/@me/relationships/{user_id}", headers=generate_headers())
        if r.status_code == 204:
            print(f"Deleted friendship with {user_id}")
        else:
            print(f"Failed to delete friendship with {user_id} - Code: {r.status_code}")

        # Close DM
        r = req.delete(f"https://discord.com/api/v9/channels/{current_channel}", headers=generate_headers())


def fetch_all_messages(user_id: str) -> list:
    print(f"Analysing {user_id}")
    fetching = True
    last_message = ""
    r = req.get(f"https://discord.com/api/v9/channels/{user_id}/messages?limit=50", headers=generate_headers())
    messages = r.json()
    message_count_this_block = 0
    user_messages = []

    for msg in messages:
        message_count_this_block += 1
        user_messages.append(msg)
    try:
        last_message = messages[message_count_this_block - 1]["id"]
    except IndexError:
        print("DM empty. Skipping!")
        return user_messages
    if message_count_this_block == 50:
        while fetching:
            time.sleep(0.25)
            r = req.get(f"https://discord.com/api/v9/channels/{user_id}/messages?before={last_message}&limit=50",
                        headers=generate_headers())
            messages = r.json()
            message_count_this_block = 0
            for msg in messages:
                message_count_this_block += 1
                user_messages.append(msg)
            try:
                last_message = messages[message_count_this_block - 1]["id"]
            except IndexError:
                print(f"IndexError... Skipping!")
                return user_messages
            if message_count_this_block < 50:
                fetching = False

    return user_messages


def main():
    valid_token = validate_token()
    if valid_token:
        print("Valid token!")
    else:
        error_catcher("invalid_token")
        quit(1)
    fetch_dms()
    unfriend_leftovers()


if __name__ == '__main__':
    main()
