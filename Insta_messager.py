
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import pandas as pd
import os
import time
import instaloader
import sqlite3
import random

global instagram_password
global instagram_username
# Instagram Credentials
instagram_username = 'tauseeq.1'
instagram_password = 'Miniclip!2345'

def random_delay(min_delay=2, max_delay=5):
    """Wait for a random time between `min_delay` and `max_delay` seconds."""
    time.sleep(random.uniform(min_delay, max_delay))

def load_session(L, username, password):
    try:
        L.load_session_from_file(username)
    except FileNotFoundError:
        # If the session file does not exist, login and create a session file
        L.login(username, password)
        L.save_session_to_file(username)

def login_to_instagram(page, username, password):
    """Logs into Instagram."""
    print("Logging in to Instagram...")
    page.goto('https://www.instagram.com/accounts/login/?next=https%3A%2F%2Fwww.instagram.com%2Flogin%2F&source=logged_out_half_sheet')
    page.wait_for_selector("input[name='username']", state="visible")
    page.fill("input[name='username']", username)
    page.fill("input[name='password']", password)
    page.click("button[type='submit']")
    random_delay(3, 5)

def send_direct_message(page, username, message):
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
                page.keyboard.press('Enter')
                print(f"Message sent to {username}.")
            else:
                print(f"Message box not found for {username}.")
        else:
            print(f"Message button not found for {username}.")
    except Exception as e:
        print(f"Failed to send a message to {username}: {e}")

def main():
    

    with sync_playwright() as p:



        # Sending messages to users in Data.csv
        username = input('ENTER USERNAME ---> ')
        message_content = input('ENTER MESSAGE ---> ')  # Define your message

        # Set headless=False to see the browser window
        browser = p.webkit.launch(headless=False)  
        page = browser.new_page()
        login_to_instagram(page, instagram_username, instagram_password)

        send_direct_message(page, username, message_content)
        random_delay(2, 5)  # Random delay to avoid being flagged as spam

    print(f"Program finished")

if __name__ == "__main__":
    main()
