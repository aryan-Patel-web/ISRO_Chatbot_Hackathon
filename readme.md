1. Brief about your Idea
My name is Aryan Patel, and I’m currently in B.Tech 3rd year at the Indian Institute of Information Technology, Manipur (IIIT). My idea is to build an AI-based Help Bot for retrieving information from a knowledge graph combining both static and dynamic ISRO data. It’s a chatbot that answers questions on missions, technologies, research papers, and news, connecting data sources like PDFs, Wikipedia, Arxiv, and live web content. Users can choose technical or simpler explanations, helping people quickly get precise ISRO insights without manually searching multiple documents.

2. What problem are you trying to solve?
Right now, information about ISRO’s missions, tech, and research is scattered across documents, websites, and news portals, making it time-consuming to find specific details. Engineers waste time searching technical docs, while students struggle with complex language. My bot solves this by unifying static and dynamic sources, letting users ask questions in natural language and instantly get technical or simplified answers.

3. Technology Stack being used
Python, LangChain, Astra DB (Cassandra), Groq’s Gemma-2b-it LLM, HuggingFace embeddings, BeautifulSoup for web scraping, Wikipedia and Arxiv tools via LangChain, and Streamlit for the frontend. I’m integrating these tools to build a conversational RAG pipeline with memory.

4. How does your solution work?
My bot loads PDFs from a “pdfread” folder or uploads, splits them into chunks, and stores embeddings in Astra DB for fast search. If local data isn’t enough, it queries Wikipedia, Arxiv, or scrapes web pages. Groq’s LLM then generates technical or simple answers based on user mode, while chat history ensures context for follow-up questions.

5. Is this your first hackathon? If No, then please share your experience.
Yes, this is my first hackathon. I’ve recently learned about generative AI, RAG, LangChain, Groq’s API, and tools like Arxiv and Wikipedia search. I’m excited to apply these skills to build something valuable for ISRO and the space tech community.







#####################


[Home Screen]
+------------------------------------+
| ISRO AI Knowledge Assistant        |
|                                    |
| [ Upload PDF ]   [ Mode: Engineer ⬇ ] |
|                                    |
| [ Search Bar: Ask your question ]  |
+------------------------------------+

↓

[Chat Screen]
+------------------------------------+
| Chat History:                      |
| User: What is GSLV heat shield?    |
| AI: [technical explanation shown]  |
|                                    |
| [ Input box for next question ]    |
+------------------------------------+




############################################





┌─────────────┐
│   User UI   │
│ (Streamlit) │
└─────┬───────┘
      │
      ▼
┌──────────────────────────────┐
│      Chat Orchestrator       │
│ (LangChain RAG Pipeline)     │
└─────┬─────────────┬──────────┘
      │             │
      │             │
      ▼             ▼
┌───────────────┐   ┌─────────────────────────┐
│  Vector Store │   │   External Tools        │
│  (Astra DB)   │   │ - Wikipedia             │
└───────────────┘   │ - Arxiv                 │
      │             │ - Web Scraping (News)   │
      ▼             └─────────────┬───────────┘
┌───────────────┐                │
│   Retriever   │◄───────────────┘
└───────────────┘
      │
      ▼
┌───────────────┐
│     LLM       │
│ (Groq Gemma)  │
└───────────────┘
      │
      ▼
┌───────────────┐
│    Answer     │
│ (Tech or Stu) │
└───────────────┘





