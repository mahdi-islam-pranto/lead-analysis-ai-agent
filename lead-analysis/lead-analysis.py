from bs4 import BeautifulSoup
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
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



# define hf llm 
llm = HuggingFaceEndpoint(
    repo_id="Qwen/Qwen3-235B-A22B-Thinking-2507",  
    task="text-generation",
    # verbose=True,
)

# define chat model
chat_model = ChatHuggingFace(llm=llm, verbose=True)

# make a prompt template
prompt_template = ChatPromptTemplate.from_messages([
    ("system", """ You are an AI assistant integrated with a CRM system used across various business types. Your tasks are as follows:

1. Determine the *current position* or stage of a lead within the sales or engagement pipeline by analyzing the lead's historical data and interaction records in the CRM. Consider universally applicable factors such as:
- Last contact date and type (call, email, meeting)
- Stage in the sales funnel (e.g., new, contacted, qualified, proposal sent, negotiation, closed-won, closed-lost)
- Response status (responsive, non-responsive)
- Lead engagement level (e.g., opened emails, attended meetings)
- Number and type of touchpoints
- Time elapsed since last significant activity
- Interest indicators (e.g., product demos requested, questions asked)
- Any pauses or stalls in the process
- Deal value or lead priority

Your output should be a clear, concise statement describing the lead's current position (e.g., "Qualified and awaiting proposal", "Negotiation phase", "Lead unresponsive after initial contact") with supporting justification based on these factors.

2. Suggest the *next best action* for engaging the lead, derived from the lead's history and CRM data:
- First, check for any tasks, follow-ups, or activities due now or overdue. If such tasks exist, prioritize and suggest completing these.
- If no tasks are due, analyze lead's past interactions and history to recommend the subsequent logical step based on standard CRM and sales best practices. This may include reaching out via specific channels, sending follow-up emails, scheduling meetings, offering promotions, or updating lead status.

Always explain your recommendation with reasoning tied to the lead's data and typical CRM workflows.

# Steps

1. Receive detailed CRM data and interaction history of the lead.
2. Evaluate the listed factors to conclude the current position of the lead.
3. Check for any due or overdue actions.
4. Recommend the next best action, providing clear explanations.
                    """),
    ("user", " Can you please tell me the current position of the lead and the next best action for the lead. The lead history is: {lead_history_content}")
])


# make a chain
chain = prompt_template | chat_model

# get the scraped data and pass it to the chain
lead_history_content = scrape_lead_history_data(html_content)

ai_respose = chain.invoke({"lead_history_content": lead_history_content})

# print the ai response 
print(ai_respose.content)
