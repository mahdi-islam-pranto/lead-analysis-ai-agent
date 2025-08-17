from fastapi import FastAPI
from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
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

    
@app.post("/leadscore")
async def root(lead_data: LeadData):

    # alternative chat model openai
    chat_model_openai = ChatOpenAI(model="gpt-5-nano")

    # define hf llm 
    llm = HuggingFaceEndpoint(
    repo_id="Qwen/Qwen3-235B-A22B-Thinking-2507",  
    task="text-generation",
    verbose=True,
    )

    # define chat model
    chat_model = ChatHuggingFace(llm=llm, verbose=True)

   # pydantic model for output
    class LeadScore(BaseModel):
        factor_scores: dict[str, int] = Field(..., description="Dictionary of scores for each factor. Key is the factor name and value is the score (out of x).")
        total_score: int = Field(..., description="Total score for the lead. (out of 100 = sum of all factor scores)")
        explanation: str = Field(..., description="Explanation of how the scores were calculated & what things are considered.")

    # Output parser for Pydantic model
    parser = PydanticOutputParser(pydantic_object=LeadScore)


    prompt_template = ChatPromptTemplate.from_messages([
    ("system", """
You are an AI Lead Scorer tool designed to analyze lead data and assign a score between 1 and 100 based on multiple relevant factors. The highest possible score is 100.

Given detailed lead data including fields such as Company Name, Website, Facebook Page, Facebook Likes and Followers, Recent Facebook Posts and Ads, Product Type, Gender Type Product, Contact Information, Industry Type, Lead Source, and others, your task is to compute a final lead score that reflects the quality and potential of the lead.

## Scoring Instructions:
- **Industry Type is the primary context:** Your scoring strategy must adapt according to the lead's Industry Type.

### For Industry Type "Ecommerce":
1. **Website Presence:** Assign a score if the lead has a website (10 points).
2. **Facebook Page Presence:** Assign a score if the lead has a Facebook page (10 points).
3. **Facebook Likes and Followers:** Score based on the number of Facebook page likes and followers; below 10,000 is low score(below 5) and over 100,000 is the highest score (above 10), scaling accordingly (15 points).
4. **Facebook Activity:** Score based on the number of posts in the last 7 days; 0 posts is lowest, 20+ posts is highest score (above 10), scaling accordingly (15 points).
5. **Product Type Demand:** Score higher for products with greater consumer demand (10 points). (do not score higher than 10)
6. **Gender Type Product:** Give higher scores if products cater to all genders, then men, then women (10 points).
7. **Ads Campaign Activity:** Score based on ads run in last 7 days. 0 is low score and over 10 ads is the highest score (20), scaling accordingly (20 points).
8. **Email Presence:** Assign score if a primary email address is available (10 points).

### For Other Industry Types (e.g., Steel Company):
- Adjust the importance and scoring weights of these factors accordingly. For example, social media presence and activity may have less impact and other factors may become more relevant.

## Scoring Methodology:
- For each relevant factor, assign a sub-score according to its importance and criteria above.
- Sum all sub-scores, then normalize or scale the total to a final score between 1 and 100.

## Task:
Using the above instructions and the provided lead data, reason through each factor step-by-step considering the Industry Type and other relevant fields. Then, compute and provide:

- The individual scores per factor
- The aggregated total score (1 to 100)
- A short explanation of how the scores were assigned


# Steps
1. Identify Industry Type.
2. For Ecommerce:
- Check website presence and assign score.
- Evaluate Facebook Page presence and followers, assign score.
- Assess Facebook activity in last 7 days for scoring.
- Analyze product type for consumer demand.
- Evaluate gender type for product appeal.
- Check for recent ads campaigns.
- Verify email availability.
3. Adjust factor weights if Industry Type differs.
4. Sum and normalize to 1-100.
5. Provide detailed scoring breakdown with explanation.


    Use clear reasoning before giving scores. Adapt scoring logic dynamically according to Industry Type.
    """),

    ("user", """ Here is the lead data:
{lead_details}
Now calculate the score out of 100.
     {format_instructions}
""")
    
    ])
        

    # make chain
    chain = prompt_template | chat_model_openai

    # prepare the lead data content
    lead_details = f"""
        Here is the Lead Details:
    {lead_data.lead_details}
        """
    
    # print(lead_details)


    # get the response from llm
    raw_ai_response = chain.invoke({"lead_details": lead_details, "format_instructions": parser.get_format_instructions()})

    # parse output into pydantic object
    parsed_output = parser.parse(raw_ai_response.content)

    # #response with structure
    # response_with_sturcture = chat_model.with_structured_output(output_json_schema)

    # get the metadata
    metadata = raw_ai_response.response_metadata
    # print(Item.data)
    return {"databody": lead_details,
            "result": parsed_output,
            "metadata": metadata
            }
