from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.document_loaders import DirectoryLoader,PyMuPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from langchain_groq import ChatGroq
import os
dir = '/'
embeddings = HuggingFaceEmbeddings(model_name='all-MiniLM-L6-v2')
groq_api_key = os.getenv('GROQ_API_KEY')

#Loading the documents
def load_docs(dir):
    loader=DirectoryLoader(dir,loader_cls=PyMuPDFLoader,use_multithreading=True,max_concurrency=128,show_progress=True,silent_errors=True)
    documents=loader.load()
    return documents

#Splitting the documents into chunks
def split_docs(documents,chunk_size=1000,chunk_overlap=100):
    text_splitter=RecursiveCharacterTextSplitter(chunk_size=chunk_size,chunk_overlap=chunk_overlap)
    docs=text_splitter.create_documents(documents)
    return docs

doc=split_docs('/p70-178.pdf')

save_to=Chroma.from_documents(documents=doc,embedding=embeddings,persist_directory='./ai-toolkit')


query="What is job "

db1=Chroma(persist_directory='./ai-toolkit',embedding_function=embeddings)
results=db1.similarity_search(query)
print(results)
print(results[0].page_content)

embeddings = SentenceTransformerEmbeddings(model_name='all-MiniLM-L6-v2')

llm=ChatGroq(groq_api_key=groq_api_key, model_name='llama3-8b-8192')

load_db=Chroma(persist_directory='./ai-toolkit',embedding_function=embeddings)

retriever=load_db.as_retriever(search_kwargs={'k':3})

template = """ You are a specialized AI assistant for the provided content.\n
    Your responses should be strictly relevant to this content/document \n
    Strictly adhere to the user's question and provide relevant information. 
    If you do not know the answer then respond "I dont know".Do not refer to your knowledge base.
    {context}
    Question:
    {question}
"""
prompt = ChatPromptTemplate.from_template(template)
output_parser = StrOutputParser()

setup_and_retrieval = RunnableParallel(
	    {"context": retriever, "question": RunnablePassthrough()}
)
chain = setup_and_retrieval | prompt | llm | output_parser

resp=chain.invoke("what is Workers’ Occupations")
print(resp)