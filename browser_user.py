import asyncio
import os
import sys
from browser_use import Agent, Browser
from langchain_google_genai import ChatGoogleGenerativeAI
import re
from dotenv import load_dotenv

load_dotenv()
task = ''
async def generate_task_and_run(keyword):
	global task
	task = f"""
	### Prompt for Browser Agent

	**Objective:**
	1. Visit google.com
	2. Formulate the query as "site:arxiv.org {keyword}"
	3. Search for the query
	4. Return the pdf link to the first research paper related to {keyword} on arxiv, only one paper.
	**Important:** Ensure efficiency and accuracy throughout the process."""
	browser = Browser()
	agent = Agent(
		task=task,
		llm=ChatGoogleGenerativeAI(model='gemini-2.0-flash-exp'),
		browser=browser,
	)

	history = await agent.run()
	await browser.close()
	# print("History:", history)# long output cant even parse it as it doesnt have history.keys()

	content = str(history)
	match = re.search(r"https?://arxiv\.org/pdf/\d+\.\d+(v\d+)?", content)
	if match:
		pdf_link = match.group(0)
		print(pdf_link)
		return pdf_link
	else:
		print("No arXiv PDF link found.")
		return None

if __name__ == "__main__":
	if len(sys.argv) < 2:
		print("Usage: python browser_user.py <keyword>")
		sys.exit(1)
	keyword = sys.argv[1]
	result = asyncio.run(generate_task_and_run(keyword))
	# The result is already printed in the function