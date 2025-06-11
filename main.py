import tweepy
import time
from datetime import datetime
from config import *

# Configure Twitter client with proper rate limiting
client = tweepy.Client(bearer_token=BEARER_TOKEN,
                       consumer_key=API_KEY,
                       consumer_secret=API_SECRET,
                       access_token=ACCESS_TOKEN,
                       access_token_secret=ACCESS_SECRET,
                       wait_on_rate_limit=True)


def post_reply(text, trigger_tweet_id):
    try:
        response = client.create_tweet(text=text[:280],
                                       in_reply_to_tweet_id=trigger_tweet_id)
        print(f"✅ Replied to {trigger_tweet_id}")
        return True
    except tweepy.TooManyRequests:
        print("⚠️ Rate limited when trying to reply - waiting 5 minutes")
        time.sleep(300)
        return False
    except Exception as e:
        print(f"❌ Reply error: {str(e)[:100]}")
        return False


def check_trusted_followers(target_user_id):
    try:
        count = 0
        with open("trusted.txt") as f:
            trusted_accounts = [line.strip() for line in f if line.strip()]

        # Check only first 3 accounts to avoid rate limits
        for account in trusted_accounts[:3]:
            try:
                user = client.get_user(username=account)
                if user.data:
                    try:
                        relationship = client.get_users_following(
                            user.data.id, max_results=100)
                        if relationship.data and any(
                                f.id == target_user_id
                                for f in relationship.data):
                            count += 1
                    except tweepy.TooManyRequests:
                        break
                time.sleep(2)  # Add delay between API calls
            except Exception as e:
                print(f"⚠️ Error checking {account}: {str(e)[:50]}")
                continue

        return min(count, 3)
    except Exception as e:
        print(f"❌ Trusted followers check error: {str(e)[:100]}")
        return 0


def analyze_user(user_id, trigger_tweet_id):
    if not user_id:
        print("⚠️ No user ID provided for analysis")
        return

    try:
        # Get basic user info
        user = client.get_user(
            id=user_id,
            user_fields=["created_at", "public_metrics", "description"])

        if not user.data:
            print("⚠️ No user data returned from API")
            return

        # Calculate account metrics
        age_days = (datetime.now() - user.data.created_at).days
        followers = user.data.public_metrics["followers_count"]
        following = user.data.public_metrics["following_count"]
        ratio = followers / max(1, following)
        bio = user.data.description
        bio_length = len(bio) if bio else 0

        # Get tweets with error handling
        try:
            tweets = client.get_users_tweets(
                user_id, max_results=10)  # Changed from 5 to 10
            avg_likes = sum(
                t.public_metrics["like_count"]
                for t in tweets.data) / len(tweets.data) if tweets.data else 0
        except:
            avg_likes = 0

        trusted_count = check_trusted_followers(user_id)

        # Generate report
        report = f"""🔍 Trust Report:
- Age: {age_days} days
- Follower Ratio: {ratio:.2f}
- Bio Length: {bio_length} chars
- Avg Likes: {avg_likes:.1f}
- Trusted Connections: {trusted_count}/3"""

        # Attempt to post reply
        return post_reply(report, trigger_tweet_id)

    except tweepy.TooManyRequests:
        print("⚠️ Rate limited during user analysis - waiting 5 minutes")
        time.sleep(300)
    except Exception as e:
        print(f"❌ User analysis error: {str(e)[:100]}")


def process_trigger(tweet):
    try:
        print(f"\n🚨 Trigger detected! Tweet ID: {tweet.id}")

        # Get the full tweet details with expansions
        full_tweet = client.get_tweet(
            tweet.id,
            expansions=["referenced_tweets.id"],
            tweet_fields=["conversation_id", "in_reply_to_user_id"])

        # Try multiple methods to find original author
        original_author = None

        # Method 1: Check referenced tweets
        if hasattr(full_tweet, 'includes') and 'tweets' in full_tweet.includes:
            for ref_tweet in full_tweet.includes['tweets']:
                if hasattr(ref_tweet, 'author_id'):
                    original_author = ref_tweet.author_id
                    break

        # Method 2: Check in_reply_to_user_id
        if not original_author and hasattr(tweet, 'in_reply_to_user_id'):
            original_author = tweet.in_reply_to_user_id

        if original_author:
            print(f"👤 Original author: {original_author}")
            analyze_user(original_author, tweet.id)
        else:
            print("⚠️ Could not determine original author")

    except tweepy.TooManyRequests:
        print("⚠️ Rate limited processing trigger - waiting 5 minutes")
        time.sleep(300)
    except Exception as e:
        print(f"❌ Trigger processing error: {str(e)[:100]}")


def monitor_replies():
    print("🔍 RUGGUARD-Bot is listening for triggers...")
    processed_tweets = set()  # Track processed tweets to avoid duplicates

    while True:
        try:
            # Increased initial delay from 60 to 300 seconds (5 minutes)
            time.sleep(300)

            print("\nChecking for new replies...")

            # Changed max_results from 5 to 10 (minimum allowed)
            replies = client.search_recent_tweets(
                query='to:projectrugguard "riddle me this" is:reply',
                max_results=10,
                expansions=["referenced_tweets.id"],
                tweet_fields=["in_reply_to_user_id"])

            if replies.data:
                print(f"Found {len(replies.data)} relevant replies")
                for reply in replies.data:
                    if reply.id not in processed_tweets:
                        processed_tweets.add(reply.id)
                        process_trigger(reply)
                        # Increased delay between processing from 15 to 60 seconds
                        time.sleep(60)
                    else:
                        print(f"⏩ Skipping already processed tweet {reply.id}")
            else:
                print("No new trigger replies found")

        except tweepy.TooManyRequests:
            print("⚠️ Rate limited on search - waiting 15 minutes")
            time.sleep(900)
        except Exception as e:
            print(f"❌ Monitoring error: {str(e)[:100]}")
            time.sleep(60)


if __name__ == "__main__":
    monitor_replies()
