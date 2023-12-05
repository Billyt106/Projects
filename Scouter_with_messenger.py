from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import pandas as pd
import os
import time
import instaloader
import random
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.tokenize import word_tokenize
from nltk import pos_tag
import spacy


global Data 
global temp

global insta_username
global password
global url

insta_username = 'tauseeq.1'  
password = 'Miniclip!2345'
url = 'https://www.instagram.com/p/Czsj5riuQIl/'
# Load spaCy model for NLP tasks
nlp = spacy.load("en_core_web_sm")

# Initialize Instaloader and Sentiment Intensity Analyzer
L = instaloader.Instaloader()

Data = 'Final_Data.csv'
temp = 'temp_data.csv'

def load_session(L, username, password):
    try:
        L.load_session_from_file(username)
    except FileNotFoundError:
        # If the session file does not exist, login and create a session file
        L.login(username, password)
        L.save_session_to_file(username)
        
def random_delay(min_delay=2, max_delay=5):
    """Wait for a random time between `min_delay` and `max_delay` seconds."""
    time.sleep(random.uniform(min_delay, max_delay))

def handle_2fa(page):
    """Handles two-factor authentication if prompted."""
    two_factor_code = input("Enter the two-factor authentication code: ")
    page.fill("input[name='verificationCode']", two_factor_code)
    page.click("button[type='submit']")
    random_delay(5, 10)  # Random delay to mimic user waiting for 2FA to process

def login_to_instagram(page, username, password):
    print("Logging in to Instagram...")
    page.goto('https://www.instagram.com/accounts/login/?next=https%3A%2F%2Fwww.instagram.com%2Flogin%2F&source=logged_out_half_sheet')
    page.wait_for_selector("input[name='username']", state="visible")
    page.fill("input[name='username']", username)
    page.fill("input[name='password']", password)
    page.click("button[type='submit']")
    random_delay(5, 10)  # Random delay to wait for login to complete
    # Check if 2FA is required
    if page.is_visible("input[name='verificationCode']"):
        handle_2fa(page)

def navigate_to_reels(page):
    """Navigates to the Instagram Reels page."""
    print("Navigating to Reels...")
    page.goto('https://www.instagram.com/reels/')
    page.wait_for_load_state('networkidle')
    print("Navigated to Reels.")


def scroll_to_next_reel(page):
    """Scrolls down to the next Instagram Reel."""
    print("Scrolling to the next Reel...")
    page.mouse.wheel(0, random.randint(300, 700))  # Random scroll distance
    random_delay(1, 3)  # Random delay after scroll
    print("Scrolled to the next Reel.")


def click_more_options_and_embed(page):
    """Clicks 'More Options', 'Embed', extracts the embed code, and extracts the username."""
    print("Clicking 'More Options' button...")
    retries = 3  # Number of retries
    retry_delay = 2  # Delay between retries in seconds
    username = None  # Initialize username to None

    for attempt in range(retries):
        more_options_button = page.query_selector('svg[aria-label="More"]')
        if more_options_button:
            more_options_button.click()
            print("Clicked 'More Options' button.")
            page.wait_for_timeout(2000)

            # Click 'Embed' and extract the embed code
            embed_button = page.query_selector('text=Embed')
            if embed_button:
                embed_button.click()
                print("Clicked 'Embed'.")
                page.wait_for_timeout(2000)
                
                # Locate the embed code textarea and extract the username
                embed_code_textarea = page.query_selector("textarea")
                if embed_code_textarea:
                    embed_code = embed_code_textarea.input_value()
                    print("Embed code extracted.")
                    username = extract_username_from_embed_code(embed_code)
                    if username:
                        print("Username extracted:", username)
                        return username  # If username is found, return it immediately
                    else:
                        print("Username could not be extracted.")
                else:
                    print("Embed code textarea not found.")
            else:
                print("'Embed' option not found.")
            break  # Break the loop if 'More Options' was found, even if no username was extracted
        else:
            print(f"'More Options' button not found, retrying... (Attempt {attempt + 1} of {retries})")
            page.wait_for_timeout(retry_delay * 1000)  # Wait before retrying
            scroll_to_next_reel(page)  # Scroll a bit to check if it triggers the button to appear

    print("Finished attempts to find 'More Options' button.")
    return username  # Return username, which will be None if not found

def extract_username_from_embed_code(embed_code):
    """Extracts the Instagram username from the embed code."""
    soup = BeautifulSoup(embed_code, "html.parser")
    a_tag = soup.find("a", string=lambda text: "A post shared by" in text if text else False)
    if not a_tag:
        return None
    text_content = a_tag.get_text(strip=True)
    username = text_content.split('@')[-1].split(')')[0].strip()
    return username

def save_username_to_csv(username, followers_count, engagement, csv_path):
    """Saves the Instagram username, follower count, and engagement to a CSV file."""
    new_row = pd.DataFrame({
        'username': [username],
        'followers_count': [followers_count],
        'engagement': [engagement]
    })
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
        df = pd.concat([df, new_row], ignore_index=True)
    else:
        df = new_row
    df.to_csv(csv_path, index=False)
    print(f"Username, followers, and engagement saved to {csv_path}")

def check_login_status(page):
    # Check if login fields are present which indicates we are logged out
    if page.is_visible("input[name='username']"):
        print("Not logged in. Attempting to log back in...")
        login_to_instagram(page, username, password)

def close_options_modal(page):
    """Closes the 'More Options' modal by clicking outside it twice."""
    print("Closing 'More Options' modal...")
    
    # Click outside the modal twice to close it
    page.mouse.click(10, 10)  # Click outside the modal (first click)
    page.wait_for_timeout(1000)
    
    page.mouse.click(10, 10)  # Click outside the modal again (second click)
    page.wait_for_timeout(1000)
    
    print("Closed 'More Options' modal.")
    
def parse_followers_count(followers_text):
    """Parse the followers count text to an integer."""
    followers_text = followers_text.lower().replace(',', '')
    multiplier = 1

    if 'k' in followers_text:
        multiplier = 1000
        followers_text = followers_text.replace('k', '')
    elif 'm' in followers_text:
        multiplier = 1000000
        followers_text = followers_text.replace('m', '')

    # For counts like '1,234' after removing 'k' or 'm'
    if '.' in followers_text:
        parts = followers_text.split('.')
        main_part = parts[0]
        decimal_part = parts[1]
        # Adjust the multiplier based on the number of decimal places
        multiplier /= 10 ** len(decimal_part)
        followers_text = main_part + decimal_part

    return int(float(followers_text) * multiplier)

def get_followers_count(page, username):
    """Gets the number of followers for a given username."""
    profile_url = f'https://www.instagram.com/{username}/'
    page.goto(profile_url)
    page.wait_for_selector('header section ul li a span', state='visible')  # Adjust the selector based on the current Instagram layout
    followers_element = page.query_selector('header section ul li a span')
    followers_count_text = followers_element.inner_text()

    # Use the helper function to parse the text to an integer
    followers_count = parse_followers_count(followers_count_text)
    return followers_count

def get_total_likes_of_last_reels(L, username, max_reels=10):
    try:
        profile = instaloader.Profile.from_username(L.context, username)
        posts = profile.get_posts()

        total_likes = 0
        count = 0

        for post in posts:
            if post.is_video and count < max_reels:
                total_likes += post.likes
                count += 1
            if count == max_reels:
                break

        return total_likes
    except instaloader.exceptions.ProfileNotExistsException:
        print(f"The profile {username} does not exist.")
        return None
    except Exception as e:
        print(f"An error occurred when getting total likes: {e}")
        return None

def get_total_comments_of_last_reels(L, username, max_reels=10):
    try:
        profile = instaloader.Profile.from_username(L.context, username)
        posts = profile.get_posts()

        total_comments = 0
        count = 0

        for post in posts:
            if post.is_video and count < max_reels:
                total_comments += post.comments
                count += 1
            if count == max_reels:
                break

        return total_comments
    except instaloader.exceptions.ProfileNotExistsException:
        print(f"The profile {username} does not exist.")
        return None
    except Exception as e:
        print(f"An error occurred when getting total comments: {e}")
        return None
    
def get_total_views_of_last_reels(L, username, max_reels=10):
    try:
        profile = instaloader.Profile.from_username(L.context, username)
        posts = profile.get_posts()

        total_views = 0
        count = 0

        for post in posts:
            if post.is_video and count < max_reels:
                total_views += post.video_view_count
                count += 1
            if count == max_reels:
                break

        return total_views
    except instaloader.exceptions.ProfileNotExistsException:
        print(f"The profile {username} does not exist.")
        return None
    except Exception as e:
        print(f"An error occurred when getting total views: {e}")
        return None

def calculate_engagement(total_likes, total_comments, total_views):
    """Calculates the engagement rate."""
    if total_views == 0:  # Prevent division by zero
        return 0
    return (total_likes + total_comments) / total_views

def check_and_relogin_if_needed(page, username, password):
    """Checks if the login page is visible, indicating a logout, and logs back in if needed."""
    if page.is_visible("input[name='username']"):  # Adjust the selector as per Instagram's layout
        print("Detected logout, attempting to log back in...")
        login_to_instagram(page, username, password)
        navigate_to_reels(page)  # Navigate back to reels after logging in

def save_top_engagements_to_final_csv(temp, Data, top_n=1):
    """Reads the CSV file, selects top N engagements, and saves to a final CSV file."""
    df = pd.read_csv(temp)
    df_sorted = df.sort_values(by='engagement', ascending=False).head(top_n)
    df_sorted.to_csv(Data, index=False)
    print('')
    print(f"Top {top_n} engagements saved to {Data}") 

def fetch_user_posts(username):
    """Fetches posts data for a given username."""
    profile = instaloader.Profile.from_username(L.context, username)
    posts_data = []

    for post in profile.get_posts():
        post_info = {
            'caption': post.caption if post.caption else "",
            'likes': post.likes,
            'comments': post.comments,
            'type': 'reel' if post.is_video else 'image',
            'url': post.url
        }
        posts_data.append(post_info)

    return posts_data

def extract_entities_and_keywords(caption):
    """Extracts entities and keywords from a caption."""
    doc = nlp(caption)
    entities = set(ent.label_ for ent in doc.ents)
    keywords = set(token.lemma_.lower() for token in doc if token.pos_ in {'NOUN', 'PROPN', 'ADJ'})
    return entities, keywords

def analyze_user_profile(posts_data):
    """Analyzes user's profile for specific themes and popular posts."""
    most_popular_post = max(posts_data, key=lambda x: x['likes'] + x['comments']) if posts_data else None
    all_entities = set()
    all_keywords = set()

    for post in posts_data:
        entities, keywords = extract_entities_and_keywords(post['caption'])
        all_entities.update(entities)
        all_keywords.update(keywords)

    return most_popular_post, all_keywords, all_entities
def type_message(page, message):
    for char in message:
        page.keyboard.type(char)
        time.sleep(0.05)  # Delay between typing each character

    time.sleep(1)  # Short pause after typing the complete message
    page.keyboard.press('Enter')
def extract_entities_and_keywords(caption):
    """Extracts entities and keywords from a caption."""
    doc = nlp(caption)
    entities = set(ent.label_ for ent in doc.ents)
    keywords = set(token.lemma_.lower() for token in doc if token.pos_ in {'NOUN', 'PROPN', 'ADJ'})
    return entities, keywords

def analyze_user_profile(posts_data):
    """Analyzes user's profile for specific themes and popular posts."""
    most_popular_post = max(posts_data, key=lambda x: x['likes'] + x['comments']) if posts_data else None
    all_entities = set()
    all_keywords = set()

    for post in posts_data:
        entities, keywords = extract_entities_and_keywords(post['caption'])
        all_entities.update(entities)
        all_keywords.update(keywords)

    return most_popular_post, all_keywords, all_entities

def generate_personalized_message(most_popular_post, all_keywords, all_entities):
    # Base message
    message = "Hey there! Just stumbled upon your profile and I must say, it's pretty awesome. "

    # Reference the most popular post in a conversational tone
    if most_popular_post and most_popular_post['caption']:
        # Remove newlines from the caption excerpt
        caption_excerpt = most_popular_post['caption'][:30].replace('\n', ' ')
        message += f"Your post '{caption_excerpt}' really caught my eye. Loved the vibe! "

    # Reference specific themes or entities
    if 'travel' in all_keywords or 'GPE' in all_entities:
        message += "The way you capture your travel adventures is just captivating. "
    if 'food' in all_keywords:
        message += "And your food posts? Simply delicious! "
    if 'music' in all_keywords:
        message += "Also, I can see we share a mutual love for music. "

    # Suggest sharing the new post
    message += f"We've also got something exciting that we think you'll love. Check it out below , it might just be your next favorite! If you enjoy it, feel free to share it on your story. We'd be thrilled, but no pressure at all. Only if it truly resonates with you. Cheers, 106 Records"

    return message

def send_direct_message(page, username, message,url):
    """Navigates to a user's Instagram profile and sends a direct message."""
    try:
        print(f"Attempting to send a message to {username}...")
        page.goto(f'https://www.instagram.com/{username}/')
        page.wait_for_load_state("networkidle")

        # Attempt to find and click the 'Message' button
        message_button_selector = "div[role='button']:has-text('Message')"
        if page.is_visible(message_button_selector):
            page.click(message_button_selector)
            random_delay(1, 3)

            # Attempt to find the message box using a detailed selector
            message_box_selector = "p[class='xat24cr xdj266r']"
            if page.wait_for_selector(message_box_selector, state="visible", timeout=5000):
                page.click(message_box_selector)
                random_delay(0.5, 1)  # Adding a brief delay before typing

                # Type the message and press Enter
                page.keyboard.type(message)
                time.sleep(3)
                page.keyboard.press('Enter')
                time.sleep(3)

                page.keyboard.type(url)
                time.sleep(3)
                page.keyboard.press('Enter')
                time.sleep(3)

                print(f"Message sent to {username}.")
            else:
                print(f"Message box not found for {username}.")
        else:
            print(f"Message button not found for {username}.")
    except Exception as e:
        print(f"Failed to send a message to {username}: {e}")
    
def main():
    threshold = 100000
    # Initialize Instaloader
    L = instaloader.Instaloader()

    with sync_playwright() as p:
        browser = p.webkit.launch(headless=False)  # Set headless=False to see the browser window
        page = browser.new_page()

        # Navigate to Instagram login page and wait for manual login
        login_to_instagram(page,insta_username,password)

        # Once logged in, continue with the rest of the script
        num_users_logged = 0
        max_users_to_log = 2  # Set to the desired number of users to log

        try:
            while num_users_logged < max_users_to_log:
                navigate_to_reels(page)
                username = click_more_options_and_embed(page)
                if username:
                    followers_count = get_followers_count(page, username)
                    if followers_count < threshold:  # Store only if followers count is less than 15k
                        total_likes = get_total_likes_of_last_reels(L, username)
                        total_comments = get_total_comments_of_last_reels(L, username)
                        total_views = get_total_views_of_last_reels(L, username)

                        if total_likes is not None and total_comments is not None and total_views is not None:
                            engagement = calculate_engagement(total_likes, total_comments, total_views)
                            save_username_to_csv(username, followers_count, engagement, temp)
                            print(f"Stored {username} with {followers_count} followers and an engagement of {engagement}.")
                            num_users_logged += 1

                    else:
                        print(f"Skipped {username} with {followers_count} followers ({threshold} or more).")

                # Scroll to next reel
                scroll_to_next_reel(page)

            # Save the top engagements to the final CSV
            if num_users_logged >= max_users_to_log:
                save_top_engagements_to_final_csv(temp, Data)
                page.goto('https://www.instagram.com/')
                time.sleep(3.1)
                temp_df = pd.read_csv(temp)
                for index, row in temp_df.iterrows():
                    username = row['username']
                    print('Getting data...')
                    posts_data = fetch_user_posts(username)
                    print('Data Retreived...')
                    print('')
                    print('Getting best posts...')
                    most_popular_post, all_keywords, all_entities = analyze_user_profile(posts_data)
                    print('Data Retreived...')
                    print('')
                    print('Generatign personalised message')
                    personalized_message = generate_personalized_message(most_popular_post, all_keywords, all_entities)
                    print('Message generated...')
                    print(personalized_message)
                    print('')
                    print('Sending message...')
                    send_direct_message(page, username, personalized_message,url)
                    print('Message sent!')
                    print('')
                    page.goto('https://www.instagram.com/')
                    time.sleep(3)

                    
        finally:
            os.remove(temp)
            print('Temp data processed and cleared.')
            print('')
            print('Program Terminated --------------> FOUNDER : TAUSEEQ SHAFQAT ')
            browser.close()
    
if __name__ == "__main__":
    main()


