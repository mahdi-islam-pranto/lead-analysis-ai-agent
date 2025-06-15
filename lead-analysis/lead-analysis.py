from bs4 import BeautifulSoup

# get the html contect from lead_page.html file
with open('lead_page.html', 'r') as f:
    html_content = f.read()

# srape lead history data function
def scrape_lead_history_data(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    history_data = soup.find('div', {'id': 'historyData'})
    all_history_data_divs = history_data.find_all('div', {'class': 'row'})
    lead_text_content = "Lead History (data and time wise): \n"
    for div in all_history_data_divs:
        text_content = div.get_text(strip=True, separator=' :')
        if text_content:
            lead_text_content += text_content + "\n"
    # print(lead_text_content)
    return lead_text_content

# srape lead details data function
scrape_lead_history_data(html_content)

