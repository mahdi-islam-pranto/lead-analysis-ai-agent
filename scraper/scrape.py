# import beautiful soup
from bs4 import BeautifulSoup

# get the html contect from lead_page.html file
with open('lead_page.html', 'r') as f:
    html_content = f.read()

# create a beautiful soup object
soup = BeautifulSoup(html_content, 'html.parser')

# get the history data div 
history_data = soup.find('div', {'id': 'historyData'})

# get the all text content of the history data div
# all_div_text_content = history_data.get_text(strip=True)

# get all the divs with class row
history_divs = history_data.find_all('div', {'class': 'row'})

# all text content variable
all_text_content = ''
# print the text content of each div
for div in history_divs:
    text_content = div.get_text(strip=True, separator=' :')
    if text_content:
        all_text_content += text_content + '\n'

print(all_text_content)



