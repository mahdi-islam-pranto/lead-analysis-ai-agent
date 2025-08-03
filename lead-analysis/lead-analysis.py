from bs4 import BeautifulSoup
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from pydantic import BaseModel, Field
from dotenv import load_dotenv
load_dotenv()

# get the html contect from lead_page.html file
with open('lead_page3.html', 'r') as f:
    html_content = f.read()

# srape lead history data function
def scrape_lead_history_data(html_content):
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
    all_text_content_for_lead = lead_info_data_h5 + '\n' + lead_info_data_p_text + '\n' + lead_pipeline_text + '\n'     + all_text_content
    print(all_text_content_for_lead)
    return all_text_content_for_lead

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
     
1. Analyze the lead's history and interaction records in the CRM and generate a short summary about this lead.

2. Determine the *current position* or stage of a lead within the sales or engagement pipeline by analyzing the lead's historical data and interaction records in the CRM. Consider universally applicable factors such as:
- Last contact date and type (call, email, meeting)
- Stage in the sales funnel (e.g., new, contacted, qualified, proposal sent, negotiation, closed-won, closed-lost)
- Response status (responsive, non-responsive)
- Lead engagement level (e.g., opened emails, attended meetings)
- Number and type of touchpoints
- Time elapsed since last significant activity
- Interest indicators (e.g., product demos requested, questions asked)
- Any pauses or stalls in the process
- Deal value or lead priority

Your output should be a clear, concise short statement describing the lead's current position (e.g., "Qualified and awaiting proposal", "Negotiation phase", "Lead unresponsive after initial contact") with supporting justification based on these factors. Justification should be short and to the point.

3. Suggest the *next best action* for engaging the lead, derived from the lead's history and CRM data:
- First, check for any tasks, follow-ups, or activities due now or overdue. If such tasks exist, prioritize and suggest completing these.
- If no tasks are due, analyze lead's past interactions and history to recommend the subsequent logical step based on standard CRM and sales best practices. This may include reaching out via specific channels, sending follow-up emails, scheduling meetings, offering promotions, or updating lead status.

Always explain your recommendation with reasoning tied to the lead's data and typical CRM workflows.
The lead history data can in bengali language.too. Try to understand the history data and make a decision. The response should be short and to the point.
# Steps

1. Receive detailed CRM data and interaction history of the lead.
2. Evaluate the listed factors to conclude the current position of the lead.
3. Check for any due or overdue actions.
4. Recommend the next best action, providing clear explanations.
                    """),
    ("user", " Can you please tell me the summary of the lead in bangla language, the current position of the lead in bangla language and the next best action for the lead in bangla language. Here is the lead's info and history: {lead_history_content}")
])

# pydantic class for the output
class LLMOutput(BaseModel):
    summary: str = Field(..., description="Summary of the lead's history")
    current_position: str = Field(..., description="Current position of the lead")
    next_best_action: str = Field(..., description="Next best action for the lead")

# convert pydantic class to json schema
output_json_schema = LLMOutput.model_json_schema()
# 
chat_model_with_structure = chat_model.with_structured_output(output_json_schema)

# make a chain
chain = prompt_template | chat_model_with_structure

# get the scraped data and pass it to the chain
lead_history_content = scrape_lead_history_data(html_content)

ai_respose = chain.invoke({"lead_history_content": lead_history_content})

# print the ai response 
print(ai_respose)