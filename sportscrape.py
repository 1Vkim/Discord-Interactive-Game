import requests
from bs4 import BeautifulSoup
import schedule
import time
import sqlite3

# Set up the SQLite database
def setup_database():
    conn = sqlite3.connect('scraped_data.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Delete old data from the database
def delete_old_data():
    conn = sqlite3.connect('scraped_data.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM articles')
    conn.commit()
    conn.close()

# Insert new data into the database
def insert_data(title):
    conn = sqlite3.connect('scraped_data.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO articles (title) VALUES (?)', (title,))
    conn.commit()
    conn.close()

# Scrape data and store it in the database
def scrape_data():
    url = "https://www.goal.com/en"
    response = requests.get(url)

    if response.status_code == 200:
        S = BeautifulSoup(response.content, "html.parser")
        articles = S.find_all('article', class_='card_card__whSYf component-card')

        if articles:
            delete_old_data()
            for article in articles:
                title = article.find('h3').text if article.find('h3') else 'No title'
                insert_data(title)
                print(title)
        else:
            print("Articles not found")
    else:
        print("Failed to retrieve the webpage")

# Scheduler
schedule.every().day.at("14:14").do(scrape_data)

def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)

# Set up the database
setup_database()

# Call the run_scheduler function to start the scheduler
run_scheduler()
