# import beautiful soup
from bs4 import BeautifulSoup

# get the html contect from lead_page.html file
with open('lead_page2.html', 'r') as f:
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
all_text_content = 'Lead History:\n'
# print the text content of each div
for div in history_divs:
    text_content = div.get_text(strip=True, separator=' :')
    if text_content:
        all_text_content += text_content + '\n'

# print("Lead's History:\n",all_text_content)

# get the lead info data
lead_info_data = soup.find_all('div', {'class': 'card'})
# get only h5 text of the first card
lead_info_data_h5 = "Lead's Company name: "+ lead_info_data[0].find('h5').get_text(strip=True)
# get all p tag of the first card

lead_info_data_p = lead_info_data[0].find_all('p')
lead_info_data_p_text = 'Lead Info:\n'
for p in lead_info_data_p:
    lead_info_data_p_text += p.get_text(strip=True) + '\n'

# get the selected option text of the lead_pipeline_change select tag
lead_pipeline_select = soup.find('select', {'id': 'lead_pipeline_change'})
# get the selected option text with a default text "Lead Pipeline: "
lead_pipeline_text = "Lead Pipeline: "
# lead_pipeline_text = None
if lead_pipeline_select:
    selected_option = lead_pipeline_select.find('option', selected=True)
    if selected_option:
        lead_pipeline_text = lead_pipeline_text + selected_option.get_text(strip=True)



# lead_info_data = lead_info_data[0].get_text(strip=True, separator=' :')

# print("Lead's Company name:",lead_info_data_h5)
# print("Lead's Info:",lead_info_data_p_text)
# print("Lead Pipeline:", lead_pipeline_text)

# combine all the text content
all_text_content_for_lead = lead_info_data_h5 + '\n' + lead_info_data_p_text + '\n' + lead_pipeline_text + '\n' + all_text_content
print(all_text_content_for_lead)
