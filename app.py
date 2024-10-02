import time
timestr = time.strftime("%Y%m%d-%H%M%S")
from PIL import Image
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import os
import uvicorn
import json
import PyPDF2
from io import BytesIO
from fastapi import FastAPI, status, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import RedirectResponse
from schema import UserOut, UserAuth
from utils import create_access_token,create_refresh_token,verify_plain_password, verify_token
from uuid import uuid4
from pdf2image import convert_from_path
from parameters import usersCollection, dataCollection
import docx
import pytesseract
pytesseract.pytesseract.tesseract_cmd = '/opt/homebrew/bin/tesseract'
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
from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import RedirectResponse
embeddings = HuggingFaceEmbeddings(model_name='all-MiniLM-L6-v2')
from fastapi.security import OAuth2PasswordBearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "FastAPI"}

from fastapi import FastAPI, status, HTTPException
from fastapi.responses import RedirectResponse
from schema import UserOut, UserAuth, TokenSchema
from rag import split_docs
from uuid import uuid4
groq_api_key = os.getenv('GROQ_API_KEY')
last_uploaded_file = None
@app.post('/signup', summary="Create new user", response_model=UserOut)
async def create_user(data: UserAuth):
    try:
        existing_user = usersCollection.find_one({"email": data.email})
        if existing_user is not None:    
            return "User already exist"
        new_user = {
            'email': data.email,
            'password': data.password,
            'id': str(uuid4())
        }
        x = usersCollection.insert_one(new_user)
        return UserOut(email=new_user['email'], id=new_user['id'])
    #     print(data, data.email, data.password, x,"\n\n")
    #     return json.dumps(x)
    except Exception as e:
        print(e)
    #     return json.dumps("ok")


@app.post('/login', response_model=TokenSchema)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    existing_user = usersCollection.find_one({"email": form_data.username})
    if existing_user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect email or password")

    hashed_pass = existing_user['password']
    if not verify_plain_password(form_data.password, hashed_pass):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect email or password")

    access_token = create_access_token(existing_user['email'])
    refresh_token = create_refresh_token(existing_user['email'])

    return TokenSchema(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"  # Include the token type here
    )


@app.post("/file/json_upload")
def upload_file(file: UploadFile):
    data = json.loads(file.file.read())
    return {"content": data,"filename": file.filename}

@app.post("/file/upload")
async def upload_file(file: UploadFile = File(...),token: str = Depends(oauth2_scheme)):
    user = verify_token(token)
    global last_uploaded_file  # Use the global variable to track the last uploaded file

    allowed_extensions = {".png", ".jpg", ".jpeg", ".pdf", ".txt", ".docx"}
    ext = os.path.splitext(file.filename)[1].lower()

    if ext not in allowed_extensions:
        raise HTTPException(status_code=400, detail="Invalid file type.")

    contents = await file.read()

    if not contents:
        return JSONResponse(status_code=400, content={"error": "File is empty."})

    try:
        if ext == ".txt":
            content_text = contents.decode('utf-8')
        elif ext in {".jpg", ".jpeg", ".png"}:
            image = Image.open(BytesIO(contents))
            content_text = pytesseract.image_to_string(image)
        elif ext == ".pdf":
            pdf_reader = PyPDF2.PdfReader(BytesIO(contents))
            content_text = ""
            for page in pdf_reader.pages:
                content_text += page.extract_text() or ""
        elif ext == ".docx":
            doc = docx.Document(BytesIO(contents))
            content_text = "\n".join([para.text for para in doc.paragraphs])
        else:
            return JSONResponse(status_code=400, content={"error": "Unsupported file format."})

        # Create a unique directory for the uploaded file
        file_name_without_ext = os.path.splitext(file.filename)[0]
        file_directory = f"./ai-toolkit/{file_name_without_ext}"
        os.makedirs(file_directory, exist_ok=True)

        # Initialize Chroma with the unique directory
        db = Chroma(persist_directory=file_directory, embedding_function=embeddings)

        # Split the content into chunks and save to the database
        chunks = split_docs([content_text])
        db.add_documents(chunks)  # You may need to implement this method if not defined

        # Store the last uploaded filename for future reference
        last_uploaded_file = file.filename

        # Redirect to ask endpoint
        return JSONResponse(content={"message": "File uploaded successfully. You can ask a question.", "ask_url": f"/ask?question="})

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/ask")
async def ask_question(question: str):
    global last_uploaded_file  # Declare the global variable here
    session_id = str(uuid4())
    if last_uploaded_file is None:
        return JSONResponse(status_code=400, content={"error": "No file has been uploaded yet."})

    # Create the directory based on the last uploaded filename to load the correct Chroma instance
    file_name_without_ext = os.path.splitext(last_uploaded_file)[0]
    file_directory = f"./ai-toolkit/{file_name_without_ext}"
    llm=ChatGroq(groq_api_key=groq_api_key, model_name='llama3-8b-8192')
    # Load Chroma instance with the specific directory
    db = Chroma(persist_directory=file_directory, embedding_function=embeddings)
    # load_db=Chroma(persist_directory='./ai-toolkit',embedding_function=embeddings)

    retriever=db.as_retriever(search_kwargs={'k':3})
    query = question
    results = db.similarity_search(query)

    if not results:
        return JSONResponse(status_code=404, content={"error": "No relevant documents found."})

    # context = results[0].page_content  # Use the most relevant chunk
    
    template = """You are a specialized AI assistant for the provided content.\n
        Your responses should be strictly relevant to this content/document.\n
        Strictly adhere to the user's question and provide relevant information. 
        If you do not know the answer then respond "I don't know". Do not refer to your knowledge base.
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
    resp = chain.invoke(question)
    data_to_insert = {
        "session_id": session_id,
        "question": question,
        "answer": resp,
        "filename": last_uploaded_file
    }
    # Insert data into MongoDB
    dataCollection.insert_one(data_to_insert)
    return {"response": resp}

if __name__ == '__main__':
    uvicorn.run(app, host = "127.0.0.1", port=8000)





