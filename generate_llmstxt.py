from firecrawl import FirecrawlApp
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize the client
firecrawl = FirecrawlApp(api_key=os.getenv("FIRECRAWL_API_KEY"))

# Generate LLMs.txt with polling
results = firecrawl.generate_llms_text(
    url="https://m.place.naver.com/restaurant/2017422925/menu/list",
    max_urls=2,
    show_full_text=True
)

# Access generation results
if results.success:
    print(f"Status: {results.status}")
    print(f"Generated Data: {results.data}")
else:
    print(f"Error: {results.error}")