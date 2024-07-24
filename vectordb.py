from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from transformers import GPT2Tokenizer

def pdf_to_retriver(archive_name):
    import PyPDF2

    def get_text_from_pdf():
        with open(f'./{archive_name}.pdf', 'rb') as pdf:
            reader = PyPDF2.PdfReader(pdf, strict=False)
            pdf_text = ""

            for page in reader.pages:
                content = page.extract_text()
                pdf_text += " "+content
        return pdf_text

    text = get_text_from_pdf()

    tokenizer = GPT2Tokenizer.from_pretrained("gpt2")

    def count_tokens(text: str) -> int:
        return len(tokenizer.encode(text))
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size = 512,
        chunk_overlap = 24,
        length_function = count_tokens,
    )

    chunks = text_splitter.create_documents([text])

    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    
    db = FAISS.from_documents(chunks, embeddings)
    retriver = db.as_retriever()
    return retriver

