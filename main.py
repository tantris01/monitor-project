from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import datetime
from os import environ
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


gum_url = 'https://www.gumtree.com.au/s-monitors/melbourne/gaming+monitor/k0c21111l3001317?price=130.00__420.00'

def find_posts(url,prev_posts = ''):
    #setting up headless chrome browser
    options = Options()
    options.headless = True
    options.add_argument("--window-size=1920,1200")

    driver = webdriver.Chrome(options=options)
    driver.get(url)

    #getting html and finding all ads
    soup = BeautifulSoup(driver.page_source,'html.parser')
    ads = soup.find_all('div',class_='user-ad-collection-new-design__wrapper--row')[0].find_all('a')
    posts = ''

    #looping through ads
    for ad in ads:
        #get ads associated info
        data = ad.get('aria-label')
        if data:
            text = data.replace(',','').split(' ')
            #search for keywords
            keywords = environ['keywords']
            print(keywords)
            if '144hz' in text or '144htz' in text or '144Hz' in text or '144 hertz' in text:    
                #creating link to ad        
                link = f"www.gumtree.com.au{ad.get('href').strip()}"
                data_split = data.split('\n')
                #formatting location data
                loc_date = data_split[2].strip().split('.')
                #formatting title data
                title = data_split[0]
                #adding to posts
                posts += f'\n{title}\n{data_split[1].strip()}\n{loc_date[0].strip()}\nDate: {loc_date[1].strip()}\n{link}\n'

    #try to find next page link            
    next_page = soup.find('a',class_ = 'page-number-navigation__link page-number-navigation__link-next link link--base-color-primary link--hover-color-none link--no-underline')
    #if next page link exists then go to the next page and re run find_posts
    if next_page:
        new_url = next_page.get('href')
        return find_posts(new_url,prev_posts+posts)
    #else quit
    driver.quit()
    return prev_posts + posts

def send_notification(posts):
    #formatting email subject
    today_date = datetime.date.today().strftime("%d:%m:%Y")
    subject = f'monitors {today_date}'

    #creating message and sending
    message = Mail(from_email = environ['MAIL_DEFAULT_SENDER'], to_emails=environ['MAIL_DEFAULT_SENDER'], subject = subject, plain_text_content=posts)
    sg = SendGridAPIClient(environ['SENDGRID_API_KEY'])
    sg.send(message)

send_notification(find_posts(gum_url))







