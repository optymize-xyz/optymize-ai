import pandas as pd
import os

from langchain_core.documents.base import Document
from langchain_community.document_loaders import TextLoader
from langchain_community.embeddings.sentence_transformer import (
    SentenceTransformerEmbeddings,
)
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import CharacterTextSplitter
from langchain_community.llms import HuggingFaceEndpoint
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain import hub
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain.chains import RetrievalQA


def get_llm():
    # Set up the Hugging Face Hub API token
    os.environ["HUGGINGFACEHUB_API_TOKEN"] = "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"

    # Define the repository ID for the Gemma 2b model
    repo_id = "google/gemma-2b-it"

    llm = HuggingFaceEndpoint(
        repo_id=repo_id, max_length=1024, temperature=1.5
    )


    df = pd.read_excel("optymize.xlsx")
    data_list = df.values.ravel().tolist()
    document_list = []

    for content in data_list:
        document = Document(content=content, page_content=content)
        document_list.append(document)
    text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=0)
    docs = text_splitter.split_documents(document_list)
    embedding_function = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
    db = Chroma.from_documents(docs, embedding_function)
    retriever = db.as_retriever(search_type="mmr", search_kwargs={'k': 4, 'fetch_k': 20})
    prompt = hub.pull("rlm/rag-prompt")

    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
    )
    return rag_chain
