from bs4 import BeautifulSoup
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from dotenv import load_dotenv
load_dotenv()


# lead data
lead_data_body = {
    "lead_details" : {
    "Company Name" : "Virgo",
    "website" : "https://www.virgo.com/",
    "Facebook Page": "https://www.facebook.com/virgoretail",
    "Facebook Page Like" : "100",
    "Facebook Followers" : "1000",
    "Last 7 day Post" : "2",
    "Product Type": "Baby Care",
    "Gender Type Product":  "ALL",
    "Last 7 day Ads" : "0",
    "Contact Name": "",
    "Contact Number": "01960888999",
    "Primary Email" : "virgoretailbd@gmail.com",
    "Industry Type" : "Ecommerce",
    "Owner" : "Abdur Rahman Emon",
    "Associate": "Azizul Hakim",
    "lead source": "Facebook",
    "lead pipeline": "New Lead",
    "lead rating" : "A Category",
    "Lead Area": "Rampura",
    "District" : "Dhaka",
    "Address" : "Plot 67, Level 3-5; DIT Road, East Hazipara, Rampura, Dhaka, Bangladesh",
    "Amount" : "",
    "remarks" : ""
    },
    "lead_history" : {
        "02 Aug 15:22 PM: Lead Create by Abdur Rahman Emon. The person said they can't do an online meeting; we have to meet in person. However, before that, I have to call him on Monday, 4/08/2025, for a meeting schedule.",
        "02 Aug 15:23 PM: Pipeline Change Create by Abdur Rahman Emon",
        "03 Aug 15:23 PM: Follow Up Create by Abdur Rahman Emon. The person changed the meeting date to 5/08/2025. I have to call him on Monday, 5/08/2025, for a in person meeting schedule."
    }
    
}


# define hf llm 
llm = HuggingFaceEndpoint(
    repo_id="Qwen/Qwen3-235B-A22B-Thinking-2507",  
    task="text-generation",
    # verbose=True,
)

# define chat model
chat_model = ChatHuggingFace(llm=llm, verbose=True)

# alternative model gpt 5 nano
chat_model_openai = ChatOpenAI(model="gpt-5-nano")

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
- Suggest the pipeline change if needed.

Always explain your recommendation with reasoning tied to the lead's data and typical CRM workflows.
The lead history data can in bengali language.too. Try to understand the history data and make a decision. The response should be short and to the point.
# Steps

1. Receive detailed CRM data and interaction history of the lead.
2. Evaluate the listed factors to conclude the current position of the lead.
3. Check for any due or overdue actions.
4. Recommend the next best action, providing clear explanations.
                    """),
    ("user", " Can you please tell me the summary of the lead in bangla language (লিড সারসংক্ষেপ:), the current position of the lead in bangla language (লিডের বর্তমান অবস্থা:) and the next best action for the lead in bangla language (পরবর্তী পদক্ষেপ :). Here is the lead's info and history: {lead_history_content}")
])

# pydantic class for the output
class LLMOutput(BaseModel):
    summary: str = Field(..., description="Summary of the lead's history")
    current_position: str = Field(..., description="Current position of the lead")
    next_best_action: str = Field(..., description="Next best action for the lead")
    

# convert pydantic class to json schema
output_json_schema = LLMOutput.model_json_schema()
# 
chat_model_with_structure = chat_model_openai.with_structured_output(output_json_schema)

# make a chain
chain = prompt_template | chat_model_with_structure


# prepare the lead history content
lead_history_content = f"""
Lead Company Name: {lead_data_body['lead_details']['Company Name']}
Lead contact name: {lead_data_body['lead_details']['Contact Name']}
Lead Industry: {lead_data_body['lead_details']['Industry Type']}
Lead Pipeline: {lead_data_body['lead_details']['lead pipeline']}
Lead History: {lead_data_body['lead_history']}
"""

# invoke the chain
ai_respose = chain.invoke({"lead_history_content": lead_history_content})

# print the ai response
print(ai_respose)

print(lead_history_content)