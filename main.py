from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import datetime
from os import environ
# from flask import Flask, render_template, request, redirect, url_for, flash
# from flask_mail import Mail, Message
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


gum_url = 'https://www.gumtree.com.au/s-monitors/melbourne/gaming+monitor/k0c21111l3001317?price=130.00__420.00'

def find_posts(url,prev_posts = ''):
    options = Options()
    options.headless = True
    options.add_argument("--window-size=1920,1200")

    driver = webdriver.Chrome(options=options)
    driver.get(url)

    soup = BeautifulSoup(driver.page_source,'html.parser')
    ads = soup.find_all('div',class_='user-ad-collection-new-design__wrapper--row')[0].find_all('a')
    posts = ''

    for ad in ads:
        data = ad.get('aria-label')
        if data:
            text = data.replace(',','').split(' ')

            if '144hz' in text or '144htz' in text or '144Hz' in text or '144 hertz' in text:            
                link = f"www.gumtree.com.au{ad.get('href').strip()}"
                data_split = data.split('\n')
                loc_date = data_split[2].strip().split('.')
                title = data_split[0]
                posts += f'\n{title}\n{data_split[1].strip()}\n{loc_date[0].strip()}\nDate: {loc_date[1].strip()}\n{link}\n'
                
    next_page = soup.find('a',class_ = 'page-number-navigation__link page-number-navigation__link-next link link--base-color-primary link--hover-color-none link--no-underline')
    if next_page:
        new_url = next_page.get('href')
        return find_posts(new_url,prev_posts+posts)
    driver.quit()
    return prev_posts + posts

def send_notification(posts):
    # app = Flask(__name__)
    # app.config['SECRET_KEY'] = 'top-secret!'
    # app.config['MAIL_SERVER'] = 'smtp.sendgrid.net'
    # app.config['MAIL_PORT'] = 587
    # app.config['MAIL_USE_TLS'] = True
    # app.config['MAIL_USERNAME'] = 'apikey'
    # app.config['MAIL_PASSWORD'] = environ['SENDGRID_API_KEY']
    # app.config['MAIL_DEFAULT_SENDER'] = environ['MAIL_DEFAULT_SENDER']
    # mail = Mail(app)    

    today_date = datetime.date.today().strftime("%d:%m:%Y")
    subject = f'monitors {today_date}'

    # with app.app_context():
    #     msg = Message(subject, recipients=[environ['MAIL_DEFAULT_SENDER']])
    #     msg.body = posts
    #     mail.send(msg)
    message = Mail(from_email = environ['MAIL_DEFAULT_SENDER'], to_emails=environ['MAIL_DEFAULT_SENDER'], subject = subject, plain_text_content=posts)
    sg = SendGridAPIClient(environ['SENDGRID_API_KEY'])
    response = sg.send(message)
    
send_notification(find_posts(gum_url))







