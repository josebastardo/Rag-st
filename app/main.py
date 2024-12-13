from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv
import os
from langchain_community.tools.tavily_search import TavilySearchResults
from pydantic import BaseModel
from pydantic.fields import Field


# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="ChatySUDo",
    description="Chat con Documentos SUD",
    version="1.0.0"
)

# Initialize OpenAI client
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL")
)

# Initialize TavilySearchResults
os.environ['TAVILY_API_KEY'] = os.getenv("TAVILY_API_KEY")
internet_search = TavilySearchResults()
internet_search.name = "internet_search"
internet_search.description = "Returns a list of relevant document snippets for a textual query retrieved from the internet."

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Setup Jinja2 templates
templates = Jinja2Templates(directory="templates")

class ChatMessage(BaseModel):
    message: str

class TavilySearchInput(BaseModel):
    query: str = Field(description="Query to search the internet with")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/chat")
async def chat(message: ChatMessage):
    # Perform internet search
    search_query = f"{message.message} site:churchofjesuschrist.org"
    search_results = internet_search.run(search_query)

    # Get OpenAI response
    response = client.chat.completions.create(
        model=os.getenv("OPENAI_MODEL"),
        messages=[
            {"role": "user", "content": message.message}
        ],
        max_tokens=50,
        temperature=0.01,
    )

    combined_response = f"Search Results:\n{search_results}\n\nChatySudo: {response.choices[0].message.content}"
    
    return {"response": combined_response}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
