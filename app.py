from dotenv import load_dotenv
from flask import Flask, render_template
import os
import facebook
import requests
from datetime import datetime


load_dotenv()
app = Flask(__name__)


app_id = os.getenv("APP_ID")
#app_secret = os.getenv("APP_SECRET")
#access_token = os.getenv("ACCESS_TOKEN")
page_access_token = os.getenv("PAGE_ACCESS_TOKEN")

graph = facebook.GraphAPI(page_access_token)

@app.route('/')
def fb_feed():
    fb_posts = []
    
    try: 
        posts = graph.get_connections(
            app_id,
            "posts",
            fields="id,message,created_time,full_picture,from{name,picture}",
            limit=10
        )
        
        while True:
            try:
                for post in posts['data']:
                    fb_posts.append({
                        'id': post['id'],
                        'message': post.get('message', ''),
                        'created_time': datetime.strptime(
                            post["created_time"], 
                            "%Y-%m-%dT%H:%M:%S%z"
                        ),
                        'image': post.get('full_picture'),
                        'username': post['from']['name'],
                        'profile_pic': post['from']['picture']['data']['url']
                    })
                
                if len(fb_posts) >= 50 or 'paging' not in posts or 'next' not in posts['paging']:
                    break
                    
                posts = requests.get(posts["paging"]["next"]).json()
                
            except Exception as e:
                print(f"Error processing page: {e}")
                break
        
        return render_template('index.html', posts=fb_posts)
        
    except facebook.GraphAPIError as e:
        return render_template('error.html', error_message=f"Facebook API Error: {e}")

if __name__ == '__main__':
    app.run()
