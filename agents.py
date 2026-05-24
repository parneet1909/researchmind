from dotenv import load_dotenv
import os

# ─────────────────────────────────────────────────────────────
# LOAD ENV
# ─────────────────────────────────────────────────────────────

load_dotenv()

# ─────────────────────────────────────────────────────────────
# LANGCHAIN IMPORTS
# ─────────────────────────────────────────────────────────────

from langchain_mistralai import ChatMistralAI

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from tools import web_search

# ─────────────────────────────────────────────────────────────
# FAST MODEL
# ─────────────────────────────────────────────────────────────

llm = ChatMistralAI(
    model="ministral-3b-latest",
    temperature=0.2,
    mistral_api_key=os.getenv("MISTRAL_API_KEY")
)

# ─────────────────────────────────────────────────────────────
# SEARCH AGENT (FAST)
# ─────────────────────────────────────────────────────────────

def build_search_agent():

    class SearchAgent:

        def invoke(self, inputs):

            query = inputs["input"]

            try:

                results = web_search(query)

                return results

            except Exception as e:

                return f"Search Error: {str(e)}"

    return SearchAgent()

# ─────────────────────────────────────────────────────────────
# READER AGENT (FAST + NO SCRAPING)
# ─────────────────────────────────────────────────────────────

def build_reader_agent():

    class ReaderAgent:

        def invoke(self, inputs):

            content = inputs["input"]

            try:

                response = llm.invoke(f"""
                Analyze and summarize the following research content.

                Focus on:
                - key insights
                - trends
                - statistics
                - important developments
                - future implications

                Research Content:
                {content}
                """)

                return response.content

            except Exception as e:

                return f"Reader Error: {str(e)}"

    return ReaderAgent()

# ─────────────────────────────────────────────────────────────
# WRITER CHAIN
# ─────────────────────────────────────────────────────────────

writer_prompt = ChatPromptTemplate.from_messages([

    (
        "system",
        """
        You are an expert research writer.

        Write concise, professional and well-structured reports.
        """
    ),

    (
        "human",
        """
Write a detailed research report.

Topic:
{topic}

Research:
{research}

Structure the report as:

- Introduction
- Key Findings
- Current Trends
- Challenges
- Future Outlook
- Conclusion
- Sources

Keep the writing professional, factual and readable.
"""
    ),
])

writer_chain = (
    writer_prompt
    | llm
    | StrOutputParser()
)

# ─────────────────────────────────────────────────────────────
# CRITIC CHAIN
# ─────────────────────────────────────────────────────────────

critic_prompt = ChatPromptTemplate.from_messages([

    (
        "system",
        """
        You are a concise and constructive research critic.
        """
    ),

    (
        "human",
        """
Review the following research report.

Report:
{report}

Provide:

Score: X/10

Strengths:
- ...

Weaknesses:
- ...

Suggestions:
- ...

Final Verdict:
...
"""
    ),
])

critic_chain = (
    critic_prompt
    | llm
    | StrOutputParser()
)