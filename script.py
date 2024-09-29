import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

SENDER_EMAIL = "emailalert82@gmail.com"   
SENDER_PASSWORD = "rynf shim bjqd vwzx" 
RECEIVER_EMAIL = "izanagiweb3@gmail.com"

def send_email(new_programs):
    
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(SENDER_EMAIL, SENDER_PASSWORD)

    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECEIVER_EMAIL
    msg['Subject'] = "New Immunefi Bug Bounty Programs"

    # Format new programs into an HTML list
    new_programs_html = "<ul>"
    for program in new_programs:
        new_programs_html += f"<li>{program}</li>"
    new_programs_html += "</ul>"

    body = f"<h2>New Immunefi Bug Bounty Programs Added:</h2>{new_programs_html}"
    msg.attach(MIMEText(body, 'html'))

    # Send the email
    server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())
    server.quit()
    
# Function to compare and find new programs
def get_new_programs(current_programs):
    try:
       # Read the previously saved programs from the CSV file
        old_programs_df = pd.read_csv('previous_programs.csv')
        old_programs = old_programs_df['Names'].tolist()
    except FileNotFoundError:
        # If the file does not exist, assume there are no previous programs
        old_programs = []
   
   # Find new programs that are in the current list but not in the old list
    new_programs = list(set(current_programs) - set(old_programs))
    # Save the current list to the CSV file for future comparisons
    pd.DataFrame({'Names': current_programs}).to_csv('previous_programs.csv', index=False)

    return new_programs

# Set up Selenium WebDriver
options = Options()
options.add_argument("--start-maximized")

driver = webdriver.Chrome(options=options)
driver.get('https://immunefi.com/bug-bounty/')

# Wait for the page to load
time.sleep(3)

# Scroll to the bottom to load all content
last_height = driver.execute_script("return document.body.scrollHeight")

while True:
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(1)
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height

# Parse the page content with BeautifulSoup
content = driver.page_source
soup = BeautifulSoup(content, 'html.parser')

program_names = []
for a in soup.findAll(attrs={'class': 'line-clamp-2'}):
    if a.get('data-testid') == 'ProjectNameCell_name':
        name = a.text.strip()
        if name not in program_names:
            program_names.append(name)

# Check for new programs
new_programs = get_new_programs(program_names)

# Send an email if there are new programs
if new_programs:
    send_email(new_programs)

df = pd.DataFrame({'Names': program_names})
df.to_csv('updated_programs.csv', index=False)

#Close the driver
driver.quit()

print("Scraping completed! Data saved to 'updated_programs.csv'.")