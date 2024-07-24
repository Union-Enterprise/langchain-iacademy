def rag(input, context=None, prompt=None, question_context={"question": None, "response": None}):
    from langchain_core.prompts import ChatPromptTemplate
    from langchain.chains.combine_documents import create_stuff_documents_chain
    from langchain.chains import create_retrieval_chain
    from vectordb import pdf_to_retriver
    from ia_model import llm
    from default_prompt import default_prompt

    default_local_prompt = default_prompt
    
    previous_question = question_context['question']
    previous_response = question_context['response']

    if prompt:
       default_local_prompt = "{input}" 

    prompt_chat = ChatPromptTemplate.from_template(default_local_prompt+"""

    Contexto: {context}
    Contexto 2 (uma pergunta feita por usuário e uma resposta gerada por você: 
        Pergunta anterior: {previous_question}
        Resposta anterior: {previous_response})
    Pergunta: {input} 
    """)
    
    document_chain = create_stuff_documents_chain(llm, prompt_chat)
    retriver = pdf_to_retriver(context)
    retriver_chain = create_retrieval_chain(retriver, document_chain)
    response = retriver_chain.invoke({"input": input, "previous_question": previous_question, "previous_response": previous_response})

    return response['answer']


if __name__ == '__main__':
    print(rag("me explique tudo sobre uma esfera", 'geometria'))