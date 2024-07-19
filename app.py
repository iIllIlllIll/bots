import os
from flask import Flask, request, redirect, jsonify
import json
import sqlite3
import requests
from oauthlib.oauth2 import WebApplicationClient

# 보안 설정 비활성화
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

app = Flask(__name__)
app.config['DEBUG'] = True  # 디버그 모드 활성화

CLIENT_ID = ''
CLIENT_SECRET = ''
REDIRECT_URI = 'http://localhost:5000/callback'
TOKEN_URL = 'https://discord.com/api/oauth2/token'
SCOPE = ["identify", "email", "guilds.join", "guilds"]
GUILD_ID = 1256209498486341646
ROLE_ID = 1256212513431879773
DISCORD_BOT_TOKEN = ''



client = WebApplicationClient(CLIENT_ID)

def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    # 테이블이 없으면 생성
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id TEXT PRIMARY KEY, username TEXT, avatar TEXT, banner TEXT, email TEXT, ip_address TEXT)''')
    conn.commit()
    conn.close()

init_db()

@app.route("/callback")
def callback():
    try:
        code = request.args.get('code')
        if code is None:
            return jsonify(error="No code provided"), 400

        # 토큰 요청 준비
        token_url, headers, body = client.prepare_token_request(
            TOKEN_URL,
            authorization_response=request.url,
            redirect_url=REDIRECT_URI,
            code=code
        )
        # 토큰 요청 보내기
        token_response = requests.post(
            token_url,
            headers=headers,
            data=body,
            auth=(CLIENT_ID, CLIENT_SECRET),
        )
        if token_response.status_code != 200:
            return jsonify(error="Failed to fetch token"), 500

        token_response_json = token_response.json()
        client.parse_request_body_response(json.dumps(token_response_json))

        # 사용자 정보 요청
        userinfo_endpoint = "https://discord.com/api/users/@me"
        uri, headers, body = client.add_token(userinfo_endpoint)
        userinfo_response = requests.get(uri, headers=headers, data=body)

        if userinfo_response.status_code != 200:
            return jsonify(error="Failed to fetch user info"), 500

        userinfo = userinfo_response.json()
        user_id = userinfo['id']
        user_ip = request.remote_addr
        store_user_info(userinfo, user_ip)

        # 역할 부여
        add_role_to_user(user_id, GUILD_ID, ROLE_ID)

        return redirect("https://discord.com")  # 인증 후 리디렉션 할 주소
    except Exception as e:
        app.logger.error(f"Error during callback: {e}")
        return jsonify(error=str(e)), 500

def store_user_info(userinfo, ip_address):
    with sqlite3.connect('users.db') as conn:
        c = conn.cursor()
        c.execute('''INSERT OR REPLACE INTO users (id, username, avatar, banner, email, ip_address)
                     VALUES (?, ?, ?, ?, ?, ?)''',
                  (userinfo['id'], userinfo['username'], userinfo['avatar'], userinfo.get('banner', None), userinfo['email'],
                   ip_address))
        conn.commit()

def add_role_to_user(user_id, guild_id, role_id):
    url = f"https://discord.com/api/v8/guilds/{guild_id}/members/{user_id}/roles/{role_id}"
    headers = {
        "Authorization": f"Bot {DISCORD_BOT_TOKEN}",
        "Content-Type": "application/json"
    }
    response = requests.put(url, headers=headers)
    if response.status_code == 204:
        print(f"Role {role_id} added to user {user_id} in guild {guild_id}")
    else:
        print(f"Failed to add role: {response.status_code}, {response.text}")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
