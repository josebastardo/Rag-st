from flask import Flask, render_template, request, jsonify
from openai import OpenAI
from dotenv import load_dotenv
import os
from langchain_community.tools.tavily_search import TavilySearchResults
from pydantic import BaseModel, Field
import markdown

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Initialize OpenAI client
client = OpenAI(
    api_key="sk-0137295be18144a39832b785cd182293",
    base_url="https://api.deepseek.com",
)

# Initialize TavilySearchResults
os.environ['TAVILY_API_KEY'] ="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"
internet_search = TavilySearchResults()
internet_search.name = "internet_search"
internet_search.description = "Returns a list of relevant document snippets for a textual query retrieved from the internet."

class TavilySearchInput(BaseModel):
    query: str = Field(description="Query to search the internet with churchofjesuschrist.org")

internet_search.args_schema = TavilySearchInput

# Store chat messages in memory (in a production environment, use a proper database)
messages = []
cache = {}

@app.route('/')
def home():
    return render_template('index.html', messages=messages)

@app.route('/chat', methods=['POST'])
def chat():
    prompt = request.json.get('message')
    if not prompt:
        return jsonify({'error': 'No message provided'}), 400

    messages.append({"role": "user", "content": prompt})

    # Check if the response is already in the cache
    if prompt in cache:
        combined_response = cache[prompt]
    else:
        try:
            # Perform internet search using TavilySearchResults
            search_query = f"{prompt} site:churchofjesuschrist.org"
            search_results = internet_search.run(search_query)

            # Format search results with clickable links
            formatted_results = "Search Results:\n\n"
            for result in search_results:
                formatted_results += f"🔗 [{result['url']}]({result['url']})\n"
                formatted_results += f"{result['content']}\n\n"

            # Combine search results with OpenAI response
            combined_response = formatted_results + "\n\nChatySudo is 📚"

            # Generate OpenAI response
            openai_response = ""
            for response in client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in messages
                ],
                max_tokens=50,  # Adjust the number of tokens
                temperature=0.01,  # Adjust the temperature
                stream=True,
            ):
                openai_response += response.choices[0].delta.content or ""

            #combined_response += f"\n\nOpenAI Response:\n{openai_response}"

            # Cache the response
            cache[prompt] = combined_response

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    # Convert the combined response to HTML using Markdown
    html_response = markdown.markdown(combined_response)

    messages.append({"role": "assistant", "content": html_response})
    return jsonify({'response': html_response})

@app.route('/clear', methods=['POST'])
def clear_chat():
    messages.clear()
    cache.clear()
    return jsonify({'status': 'success'})

if __name__ == '__main__':
    app.run(debug=True)
