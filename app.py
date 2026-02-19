from dotenv import load_dotenv
from flask import Flask, render_template
import os
import facebook
import requests
import logging
from datetime import datetime

#uncomment this for logging the data
#logging.basicConfig(filename='app.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s', filemode='a')

load_dotenv()
app = Flask(__name__)

#ennviroment variable for personal account
#app_secret = os.getenv("APP_SECRET")
#access_token = os.getenv("ACCESS_TOKEN")

page_id = os.getenv("PAGE_ID")
page_access_token = os.getenv("PAGE_ACCESS_TOKEN")

if not page_id:
    raise ValueError("Missing Page ID Enviroment Variables")

if not page_access_token:
    raise ValueError("Missing Page Token Enviroment Variables")


graph = facebook.GraphAPI(access_token=page_access_token)

@app.route('/')
def fb_feed():
    fb_posts = []
    
    try: 
        posts = graph.get_connections(
            page_id,
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
        
        #uncomment to log
        #logging.debug(fb_posts)
        return render_template('index.html', posts=fb_posts)
        
    except facebook.GraphAPIError as e:
        return render_template('error.html', error_message=f"Facebook API Error: {e}")

if __name__ == '__main__':
    app.run()
