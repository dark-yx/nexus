
import chromadb
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain.document_loaders import TextLoader
from langchain.llms import OpenAI

class RAG:
    def __init__(self, api_key):
        self.client = chromadb.Client()
        self.embedding_function = OpenAIEmbeddings(openai_api_key=api_key)
        self.llm = OpenAI(openai_api_key=api_key)

    def load_document(self, file_path):
        loader = TextLoader(file_path)
        documents = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
        texts = text_splitter.split_documents(documents)
        self.vectorstore = Chroma.from_documents(texts, self.embedding_function)
        self.qa = RetrievalQA.from_chain_type(llm=self.llm, chain_type="stuff", retriever=self.vectorstore.as_retriever())

    def query(self, query):
        return self.qa.run(query)
