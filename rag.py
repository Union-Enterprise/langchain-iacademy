from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from vectordb import pdf_to_retriver
from main import llm

prompt = ChatPromptTemplate.from_template("""Responda a pergunta com base apenas no contexto, utilize uma linguagem simples mas que mantenha a resposta concisa e didática, explique também conceitos não muito conhecidos:
{context}
Pergunta: {input} 
""")

document_chain = create_stuff_documents_chain(llm, prompt)
retriver = pdf_to_retriver('geometria')
retriver_chain = create_retrieval_chain(retriver, document_chain)
response = retriver_chain.invoke({"input": "me explique tudo sobre uma esfera"})
print(response['answer'])