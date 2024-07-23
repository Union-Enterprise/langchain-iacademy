from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from vectordb import pdf_to_retriver
from ia_model import llm

prompt = ChatPromptTemplate.from_template("""
Responda a pergunta apenas usando o contexto(não precisa usar nada da sua base de conhecimento) e seguindo as seguintes orientações:                                          

Quero que aja como um professor de um adolescente que está estudando para o ENEM, uma prova de vestibular brasileiro.
Eu irei te enviar apenas o tema (e.g Triângulos na Geometria Plana) e você deve me retornar informações organizadas sobre o assunto, entendido?
Quero que explique detalhadamente, sem conselhos e modéstias, seja direto ao ponto.
Caso encontre alguma palavra pouco conhecida, sinalize ela para que eu possa tratar dela e exibir o resultado para meu usuário.
Não precisa me explicar sobre triângulos agora, só nas próximas vezes que eu solicitar e enviar algum conteúdo.
Não quero um resumo básico, quero que você se aprofunde no tema.
Você será o alimentador de um portal de trilhas de conhecimento, onde, cada tópico contém assuntos, por exemplo, dentro de "Geometria Plana", há "Quadrados", "Triângulos", "Trapézios" etc. Logo, não há a necessidade de explicar conceitos como "Teorema de Pitágoras" dentro do assunto "Quadrado", pois ele será abordado no assunto "Triângulos"
Não aja como uma inteligência artificial, pois, meu usuário não terá acesso à você, então não trate como se, após seu output, o usuário ainda consiga comunicar contigo, pois ele não conseguirá. Por exemplo, sem: "Avise-me se desejar explorar algum aspecto específico com mais detalhes ou se tiver qualquer dúvida!"

Contexto: {context}
Pergunta: {input} 
""")

document_chain = create_stuff_documents_chain(llm, prompt)
retriver = pdf_to_retriver('geometria')
retriver_chain = create_retrieval_chain(retriver, document_chain)
response = retriver_chain.invoke({"input": "me explique tudo sobre uma esfera"})
print(response['answer'])