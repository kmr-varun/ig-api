from typing import Dict
import json
import httpx
import jmespath
from urllib.parse import quote
from flask import Flask, jsonify, request
from jsonmerge import merge
from flask_cors import CORS, cross_origin


app = Flask(__name__)
CORS(app)

client = httpx.Client(
    headers={
        "x-ig-app-id": "936619743392459",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9,ru;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept": "*/*",
    }
)

def scrape_user(username: str):
    result = client.get(
        f"https://i.instagram.com/api/v1/users/web_profile_info/?username={username}",
    )
    data = json.loads(result.content)
    return data["data"]["user"]

def parse_user(data: Dict) -> Dict:
    result = jmespath.search(
        """{
        name: full_name,
        username: username,
        id: id,
        followers: edge_followed_by.count,
        follows: edge_follow.count,
        is_private: is_private,
        is_verified: is_verified,
        profile_image: profile_pic_url_hd,
        video_count: edge_felix_video_timeline.count,
        image_count: edge_owner_to_timeline_media.count
    }""",
        data,
    )
    return result

def parse_post(data: Dict) -> Dict:
    result = jmespath.search("""{
        id: id,
        shortcode: shortcode,
        src: display_url,
        video_url: video_url,
        views: video_view_count,
        plays: video_play_count,
        likes: edge_media_preview_like.count,
        is_video: is_video,
        comments_count: edge_media_to_parent_comment.count
    }""", data)
    return result

def scrape_user_posts(user_id: str, session: httpx.Client, page_size=12):
    base_url = "https://www.instagram.com/graphql/query/?query_hash=e769aa130647d2354c40ea6a439bfc08&variables="
    variables = {
        "id": user_id,
        "first": page_size,
        "after": None,
    }
    _page_number = 1
    while True:
        resp = session.get(base_url + quote(json.dumps(variables)))
        data = resp.json()
        posts = data["data"]["user"]["edge_owner_to_timeline_media"]
        for post in posts["edges"]:
            yield parse_post(post["node"])
        page_info = posts["page_info"]
        if _page_number == 1:
            print(f"scraping total {posts['count']} posts of {user_id}")
        else:
            print(f"scraping page {_page_number}")
        if not page_info["has_next_page"]:
            break
        if variables["after"] == page_info["end_cursor"]:
            break
        variables["after"] = page_info["end_cursor"]
        _page_number += 1

@app.route('/user/', methods=['GET'])
def error_user():
    return "Enter User Name"

@app.route('/posts/', methods=['GET'])
def error_post():
    return "Enter User ID"

@app.route('/posts/<int:user_id>', methods=['GET'])
def get_posts(user_id):
        with httpx.Client(timeout=httpx.Timeout(20.0)) as session:
            posts = list(scrape_user_posts(user_id, session))
            return json.dumps(posts, indent=2, ensure_ascii=False)

@app.route('/user/<string:user_name>', methods=['GET'])
def get_user(user_name):
    userdata = parse_user(scrape_user(user_name))        
    return json.dumps(userdata, indent=2, ensure_ascii=False)


if __name__ == '__main__':
    app.run(debug=True)