from fastapi import FastAPI
from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from pydantic import BaseModel, Field
from dotenv import load_dotenv
load_dotenv()
app = FastAPI()

class Item(BaseModel):
    data: dict
    

@app.post("/leadscore")
async def root(Item: Item):

    prompt_template = ChatPromptTemplate.from_messages([
    ("system", """
You are an AI Lead Scorer tool designed to analyze lead data and assign a score between 1 and 100 based on multiple relevant factors. The highest possible score is 100.

Given detailed lead data including fields such as Company Name, Website, Facebook Page, Facebook Likes and Followers, Recent Facebook Posts and Ads, Product Type, Gender Type Product, Contact Information, Industry Type, Lead Source, and others, your task is to compute a final lead score that reflects the quality and potential of the lead.

## Scoring Instructions:
- **Industry Type is the primary context:** Your scoring strategy must adapt according to the lead's Industry Type.

### For Industry Type "Ecommerce":
1. **Website Presence:** Assign a score if the lead has a website.
2. **Facebook Page Presence:** Assign a score if the lead has a Facebook page.
3. **Facebook Likes and Followers:** Score based on the number of Facebook page likes and followers; below 10,000 is low score and over 100,000 is the highest score, scaling accordingly.
4. **Facebook Activity:** Score based on the number of posts in the last 7 days; 0 posts is lowest, 20+ posts is highest score.
5. **Product Type Demand:** Score higher for products with greater consumer demand.
6. **Gender Type Product:** Give higher scores if products cater to all genders, then men, then women.
7. **Ads Campaign Activity:** Score based on ads run in last 7 days. 0 is low score and over 10 is the highest score, scaling accordingly.
8. **Email Presence:** Assign score if a primary email address is available.

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
Now calculate the score.
""")
    
    ])

    # define hf llm 
    llm = HuggingFaceEndpoint(
    repo_id="Qwen/Qwen3-235B-A22B-Thinking-2507",  
    task="text-generation",
    verbose=True,
    )

    # define chat model
    chat_model = ChatHuggingFace(llm=llm, verbose=True)

# make a openai llm
# llm = ChatOpenAI(
#     model="gpt-4o",
#     temperature=0.2,
# )

# pydantic model for output

    class LeadScore(BaseModel):
        factor_scores: dict[str, int] = Field(..., description="Dictionary of scores for each factor. Key is the factor name and value is the score (out of x).")
        total_score: int = Field(..., description="Total score for the lead. (out of 100 = sum of all factor scores)")
        explanation: str = Field(..., description="Explanation of how the scores were calculated")

    # convert pydantic class to json schema
    output_json_schema = LeadScore.model_json_schema()

    #response with structure
    response_with_sturcture = chat_model.with_structured_output(output_json_schema)

    result = response_with_sturcture.invoke(prompt_template.invoke({"lead_details": Item.data}))
    # print(Item.data)
    return {"databody": Item.data,
            "result": result
            }
