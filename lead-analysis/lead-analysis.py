from bs4 import BeautifulSoup
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from dotenv import load_dotenv
load_dotenv()

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
    print(lead_text_content)
    return lead_text_content

# srape lead details data function
# scrape_lead_history_data(html_content)



# make llm 
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.2)

# make a prompt template
prompt_template = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant that can analyze lead history and give a score to the lead. The score vary from 0 to 10. 0 is the worst and 10 is the best. There are some factor that can affect the lead score. If the lead is very old and still any task for that lead is not done then the score should be very low. Same goes for the follow up. The details of the tasks and followup can be in bangla language."),
    ("user", "Can you please give a score to the following lead? Also give the reason for the score. Then suggest some action for the lead. Try to make the response short. The lead history is: {lead_history_content}")
])


# make a chain
chain = prompt_template | llm

# get the scraped data and pass it to the chain
lead_history_content = scrape_lead_history_data(html_content)

ai_respose = chain.invoke({"lead_history_content": lead_history_content})

# print the ai response 
print(ai_respose.content)

