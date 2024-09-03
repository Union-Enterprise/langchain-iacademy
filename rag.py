class LLMlearning:
    def __init__(self, context):
        from vectordb import pdf_to_retriver, txt_to_retriver
        from os import path

        self.context = context
        
        if path.isfile(f'contexts/{self.context}.txt'):
            self.retriver = txt_to_retriver(self.context)
        else:
            self.retriver = pdf_to_retriver(self.context)


    def ask(self, input_user, question_context={"question": None, "response": None}, prompt=None):
        from langchain_core.prompts import ChatPromptTemplate
        from langchain.chains import create_retrieval_chain
        from langchain.chains.combine_documents import create_stuff_documents_chain
        from default_prompt import default_prompt

        from ia_model import llm


        default_local_prompt = prompt if prompt else default_prompt

        prompt_chat = ChatPromptTemplate.from_template(
            default_local_prompt + """
            \nContexto: {context}
            \nContexto 2 (uma pergunta feita por usuário e uma resposta gerada por você:
            \nPergunta anterior: {previous_question} 
            \nResposta anterior: {previous_response})\n
            \nPergunta: {input}
            """
        )

        document_chain = create_stuff_documents_chain(llm, prompt_chat)
        retriever_chain = create_retrieval_chain(self.retriver, document_chain)
        
        response = retriever_chain.invoke({
            "input": input_user,
            "previous_question": question_context["question"],
            "previous_response": question_context["response"],
            "context": self.context
        })

        return response['answer']


if __name__ == '__main__':
    geometria = LLMlearning('geometria')
    print(geometria.ask("me explique tudo sobre uma esfera"))
    print(geometria.ask("me explique tudo sobre cubos"))
