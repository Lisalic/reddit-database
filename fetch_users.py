import sqlite3
import time
import praw
import os  

ID = os.environ.get("REDDIT_ID")
SECRET = os.environ.get("REDDIT_SECRET")

if not ID or not SECRET:
    print("Error: REDDIT_ID and REDDIT_SECRET environment variables not set.")
    print("Please set them before running the script:")
    print("  export REDDIT_ID='your_client_id'")
    print("  export REDDIT_SECRET='your_client_secret'")
    exit(1)  

reddit = praw.Reddit(
    client_id=ID,
    client_secret=SECRET,
    user_agent="userinfo_script"
)

DB_PATH = "reddit_data.db"
BATCH_SIZE = 100
SLEEP_SEC = 0.3 

def create_users_tables(conn):
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS reddit_users (
        id TEXT PRIMARY KEY,
        username TEXT NOT NULL,
        created_utc INTEGER,
        comment_karma INTEGER,
        link_karma INTEGER,
        is_mod BOOLEAN,
        is_suspended BOOLEAN,
        profile_name TEXT,
        profile_description TEXT,
        retrieved_on INTEGER
    )
    ''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS reddit_users_failed (
        username TEXT PRIMARY KEY,
        reason TEXT,
        retrieved_on INTEGER
    )
    ''')
    conn.commit()

def get_unique_users(conn):
    cursor = conn.cursor()
    cursor.execute('''
    SELECT DISTINCT author FROM (
        SELECT author FROM submissions
        UNION
        SELECT author FROM comments
    )
    ''')
    return [row[0] for row in cursor.fetchall() if row[0] != "[deleted]"]

def fetch_and_store_users(conn, usernames):
    cursor = conn.cursor()
    total = len(usernames)

    cursor.execute('SELECT username FROM reddit_users')
    existing_users = set(row[0] for row in cursor.fetchall())

    cursor.execute('SELECT username FROM reddit_users_failed')
    failed_users = set(row[0] for row in cursor.fetchall())

    usernames_to_fetch = [u for u in usernames if u not in existing_users and u not in failed_users]
    removed_count = len(usernames) - len(usernames_to_fetch)
    if removed_count > 0:
        print(f"Skipped {removed_count} users already in DB or failed previously.")

    batch_success = []
    batch_failed = []
    batch_count = 0
    additions = 0
    errors = 0
    skipped = 0

    for i, username in enumerate(usernames_to_fetch, start=1):
        try:
            user = reddit.redditor(username)
            user_id = getattr(user, "id", None)

            if not user_id:
                batch_failed.append((username, "suspended_or_none", int(time.time())))
                skipped += 1
                continue

            is_suspended = getattr(user, "is_suspended", False)
            profile_subreddit = getattr(user, "subreddit", None)
            profile_name = getattr(profile_subreddit, "display_name", None) if profile_subreddit else None
            profile_description = getattr(profile_subreddit, "public_description", None) if profile_subreddit else None

            batch_success.append((
                user_id,
                username,
                getattr(user, "created_utc", None),
                getattr(user, "comment_karma", None),
                getattr(user, "link_karma", None),
                getattr(user, "is_mod", None),
                is_suspended,
                profile_name,
                profile_description,
                int(time.time())
            ))
            additions += 1

        except Exception as e:
            batch_failed.append((username, str(e), int(time.time())))
            errors += 1

        if len(batch_success) + len(batch_failed) >= BATCH_SIZE:
            if batch_success:
                cursor.executemany('''
                    INSERT OR REPLACE INTO reddit_users
                    (id, username, created_utc, comment_karma, link_karma, is_mod, is_suspended, profile_name, profile_description, retrieved_on)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', batch_success)
            if batch_failed:
                cursor.executemany('''
                    INSERT OR REPLACE INTO reddit_users_failed
                    (username, reason, retrieved_on)
                    VALUES (?, ?, ?)
                ''', batch_failed)
            conn.commit()
            batch_count += 1
            print(f"Batch {batch_count}: Added {additions}, Skipped {skipped}, Errors {errors}")
            batch_success.clear()
            batch_failed.clear()
            additions = 0
            errors = 0
            skipped = 0
            time.sleep(SLEEP_SEC)

    if batch_success or batch_failed:
        if batch_success:
            cursor.executemany('''
                INSERT OR REPLACE INTO reddit_users
                (id, username, created_utc, comment_karma, link_karma, is_mod, is_suspended, profile_name, profile_description, retrieved_on)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', batch_success)
        if batch_failed:
            cursor.executemany('''
                INSERT OR REPLACE INTO reddit_users_failed
                (username, reason, retrieved_on)
                VALUES (?, ?, ?)
            ''', batch_failed)
        conn.commit()
        batch_count += 1
        print(f"Final Batch {batch_count}: Added {additions}, Skipped {skipped}, Errors {errors}")

def main():
    conn = sqlite3.connect(DB_PATH)
    create_users_tables(conn)
    usernames = get_unique_users(conn)
    print(f"Found {len(usernames)} unique users.")
    fetch_and_store_users(conn, usernames)
    conn.close()
    print("All user data fetched and stored.")

if __name__ == "__main__":
    main()