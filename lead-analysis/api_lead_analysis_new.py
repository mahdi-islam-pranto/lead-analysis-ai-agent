from fastapi import FastAPI
from langchain.prompts import ChatPromptTemplate
from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace
from langchain_openai import ChatOpenAI
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from dotenv import load_dotenv
load_dotenv()

app = FastAPI()

# sample lead data for Api body (testing)
lead_data_body = {
    "lead_details" : {
    "company_name" : "Virgo",
    "website" : "https://www.virgo.com/",
    "facebook_page": "https://www.facebook.com/virgoretail",
    "facebook_page_like" : "100",
    "facebook_followers" : "1000",
    "last_7_day_post" : "2",
    "product_type": "Baby Care",
    "gender_type_product":  "ALL",
    "last_7_day_ads" : "0",
    "contact_name": "",
    "contact_number": "01960888999",
    "primary_email" : "virgoretailbd@gmail.com",
    "industry_type" : "Ecommerce",
    "owner" : "Abdur Rahman Emon",
    "associate": "Azizul Hakim",
    "lead_source": "Facebook",
    "lead_pipeline": "New Lead",
    "lead_rating" : "A Category",
    "lead_area": "Rampura",
    "district" : "Dhaka",
    "address" : "Plot 67, Level 3-5; DIT Road, East Hazipara, Rampura, Dhaka, Bangladesh",
    "amount" : "",
    "remarks" : ""
    },
    "lead_history" : [
        "02 Aug 15:22 PM: Lead Create by Abdur Rahman Emon. The person said they can't do an online meeting; we have to meet in person. However, before that, I have to call him on Monday, 4/08/2025, for a meeting schedule.",
        "02 Aug 15:23 PM: Pipeline Change Create by Abdur Rahman Emon",
        "03 Aug 15:23 PM: Follow Up Create by Abdur Rahman Emon. The person changed the meeting date to 5/08/2025. I have to call him on Monday, 5/08/2025, for a in person meeting schedule."
    ]
    
}

# pydantic class for the input
class LeadData(BaseModel):
    lead_details: dict
    lead_history: list


# API end point
@app.post("/leadanalysis")
async def create_lead_analysis(lead_data: LeadData):
    
    try:        

        # pydantic class for the output
        class LLMOutput(BaseModel):
            summary: str = Field(..., description="Summary of the lead's history")
            current_position: str = Field(..., description="Current position of the lead")
            next_best_action: str = Field(..., description="Next best action for the lead")
    
        # define hf llm 
        llm = HuggingFaceEndpoint(
            repo_id="Qwen/Qwen3-235B-A22B-Thinking-2507",  
            task="text-generation",
            # verbose=True,
        )

        # define chat model
        chat_model = ChatHuggingFace(llm=llm, verbose=True)

        # alternative chat model openai
        chat_model_openai = ChatOpenAI(model="gpt-5-nano")

        # Output parser for Pydantic model
        parser = PydanticOutputParser(pydantic_object=LLMOutput)

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
        The lead history data can in Bangla language too. Try to understand the history data and make a decision. The response should be short and to the point.
        # Steps

        1. Receive detailed CRM data and interaction history of the lead.
        2. Evaluate the listed factors to conclude the current position of the lead.
        3. Check for any due or overdue actions.
        4. Recommend the next best action, providing clear explanations.
        
                        """),
        ("user", """ Can you please tell me the summary of the lead in bangla language, the current position of the lead in bangla language and the next best action for the lead in bangla language. Here is the lead's info and history: {lead_history_content}
         {format_instructions}
         """),
        
        ])

        


        # # convert pydantic class to json schema
        # output_json_schema = LLMOutput.model_json_schema()
        # # make a chat model with structured output
        # chat_model_with_structure = chat_model_openai.with_structured_output(output_json_schema)

        # make a chain
        chain = prompt_template | chat_model_openai


        

        # get the lead data from the input (api body)
        # prepare the lead history content
        lead_history_content = f"""
        Lead Details:
        Lead Company Name: {lead_data.lead_details['company_name']}
        Lead contact name: {lead_data.lead_details['contact_name']}
        Lead Industry: {lead_data.lead_details['industry_type']}
        Lead Pipeline: {lead_data.lead_details['lead_pipeline']}
        Lead History by date: {lead_data.lead_history}
    """

        # get the response from the llm
        raw_ai_response = chain.invoke({"lead_history_content": lead_history_content,
                                        "format_instructions": parser.get_format_instructions()
                                        })
         # Parse output into Pydantic object
        structured_output = parser.parse(raw_ai_response.content)

        # Get metadata
        metadata = raw_ai_response.response_metadata

        # print(history_data)
        return {"lead_history_data": lead_history_content,
                "ai_response": structured_output.model_dump(),
                "metadata": metadata
                }
    
    except Exception as e:
        return {"Error": str(e)}