import praw
import json
import time
from prawcore.exceptions import TooManyRequests

# Replace these with your actual credentials
client_id = "###############" # Your client_id
client_secret = "################"        # Your client_secret from Reddit app
user_agent = "RedditPostFetcher"  # Your custom user agent

# Set up Reddit API client
reddit = praw.Reddit(client_id=client_id,
                     client_secret=client_secret,
                     user_agent=user_agent)

def fetch_posts(subreddits, output_file):
    all_posts = []
    
    for subreddit in subreddits:
        subreddit_obj = reddit.subreddit(subreddit)
        
        try:
            # Fetch posts
            for post in subreddit_obj.new(limit=None):  # Fetch new posts; use `.top()` for top posts
                post_data = {
                    "subreddit": subreddit,  # Add subreddit name
                    "title": post.title,
                    "id": post.id,
                    "created_utc": post.created_utc,
                    "score": post.score,
                    "url": post.url,
                    "comments_count": post.num_comments,
                    "text": post.selftext,  # The text content of the post
                    "comments": []
                }

                # Fetch comments for the post
                try:
                    post.comments.replace_more(limit=0)  # Replace 'MoreComments' objects
                    for comment in post.comments.list():  # Loop through comments
                        post_data["comments"].append({
                            "author": str(comment.author),
                            "body": comment.body,
                            "score": comment.score
                        })
                except TooManyRequests:
                    print(f"Rate limit hit while fetching comments for post {post.id}. Waiting for 60 seconds...")
                    time.sleep(60)
                    continue

                # Append post data
                all_posts.append(post_data)

        except TooManyRequests:
            print(f"Rate limit hit while fetching subreddit {subreddit}. Waiting for 60 seconds...")
            time.sleep(60)
            continue

    # Save to file
    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(all_posts, file, indent=4, ensure_ascii=False)

    print(f"Fetched {len(all_posts)} posts from {', '.join(subreddits)}. Saved to {output_file}.")

# List of subreddits
subreddits = ["CureAphantasia", "Hyperphantasia", "Aphantasia"]

# Fetch posts
fetch_posts(subreddits, "subreddit_posts.json")
