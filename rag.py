import os
import re
import fitz
from pymongo import MongoClient
from dotenv import load_dotenv
from pprint import pprint
from langchain import LLMChain
from langchain.prompts import PromptTemplate
import ast
# from langchain.llms import Gemini

from ia_model import llm

load_dotenv()

class LLMlearning:
    def __init__(self, context):
        self.context = context
        self.llm = llm
        
    def connect_to_mongodb(self):
        client = MongoClient(os.environ.get("CONNECTION_STRING"))
        db = client['iacademy']
        return db

    def extract_text_from_pdf(self, pdf_path):
        doc = fitz.open(pdf_path)
        text = ""
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text += page.get_text() + "\n"
        return text

    def clean_text(self, text):
        return re.sub(r'\s+', ' ', text).strip()

    def extract_images_from_page(self, page, question_num, save_dir='images', img_counter=0):
        os.makedirs(save_dir, exist_ok=True)
        image_paths = []
        image_list = page.get_images(full=True)
        
        for img_index, img in enumerate(image_list):
            xref = img[0]
            base_image = page.parent.extract_image(xref)
            image_bytes = base_image["image"]
            image_ext = base_image["ext"]
            image_path = os.path.join(save_dir, f"image_{question_num}_{img_counter + 1}.{image_ext}")
            
            with open(image_path, "wb") as img_file:
                img_file.write(image_bytes)
            
            image_paths.append(image_path)
            img_counter += 1
        
        return image_paths, img_counter

    def replace_image_descriptions(self, page_text, descriptions, imagens):
        for i, descricao in enumerate(descriptions):
            imagem_path = imagens[i] if i < len(imagens) else None
            if imagem_path:
                imagem_tag = f"<imagem {imagem_path}>"
                page_text = page_text.replace(descricao, imagem_tag)
        return page_text

    def extract_questions_from_pdf(self, pdf_path):
        doc = fitz.open(pdf_path)
        img_counter = 0
        all_questions = []
        current_question = None
        question_num = 1

        question_start_pattern = r"(QUESTÃO\s+\d+)"
        description_pattern = r"(Descrição (?:da|do) (?:figura|gráfico|mapa|quadrinho|imagem|quadro|esquema|alternativas|foto|tabela):.*?\(Fim da descrição\))"
        alternatives_pattern = r"\b([a-e])\.\s+"

        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            page_text = page.get_text()

            page_text = self.clean_text(page_text)

            question_starts = re.findall(question_start_pattern, page_text)

            if question_starts:
                if current_question:
                    all_questions.append(current_question)
                    question_num += 1

                current_question = {
                    "titulo": f"Questão {question_num}",
                    "descricao_figura": [],
                    "alternativa_descricao": "",
                    "questao": "",
                    "imagens": [],
                    "alternativas": [],
                    "alternativa_correta": "" 
                }

            if current_question:
                current_question["questao"] += f" {page_text}"

            descriptions = re.findall(description_pattern, page_text, re.DOTALL)

            if descriptions and current_question:
                for description in descriptions:
                    cleaned_description = self.clean_text(description)
                    if "alternativas" in cleaned_description:
                        current_question["alternativa_descricao"] = cleaned_description
                    else:
                        current_question["descricao_figura"].append(cleaned_description)

                    image_paths, img_counter = self.extract_images_from_page(page, question_num, img_counter=img_counter)
                    current_question["imagens"].extend(image_paths)

            alternatives_split = re.split(alternatives_pattern, page_text)
            if current_question and not current_question["questao"]:
                current_question["questao"] = alternatives_split[0].strip()

            alternatives_found = False
            expected_alternative = 'a'
            valid_alternatives = []
            
            for j in range(1, len(alternatives_split) - 1, 2):
                alternative_letter = alternatives_split[j].lower()
                alternative_text = alternatives_split[j + 1].strip()

                if current_question and alternative_letter == expected_alternative:
                    current_question["alternativas"].append(f"{alternative_letter}. {alternative_text}")
                    valid_alternatives.append(f"{alternative_letter}. {alternative_text}")
                    alternatives_found = True
                    expected_alternative = chr(ord(expected_alternative) + 1) 
                else:
                    break

            if current_question:
                for i in range(len(current_question["descricao_figura"])):
                    if i < len(current_question["imagens"]):
                        imagem_tag = f"<imagem {current_question['imagens'][i]}>"
                        current_question["questao"] = current_question["questao"].replace(current_question["descricao_figura"][i], imagem_tag)

            if alternatives_found and current_question:
                for alt in valid_alternatives:
                    alt_escaped = re.escape(alt)
                    current_question["questao"] = re.sub(rf"\s*{alt_escaped}\s*", "", current_question["questao"])

        if current_question and current_question["questao"]:
            all_questions.append(current_question)

        return all_questions

    def generate_quiz_by_pdf(self, pdf_path):
        questions = self.extract_questions_from_pdf(pdf_path)
        return questions

    def send_questions_to_gemini(self, questions):
        for question in questions:
            prompt_template = """{titulo}\n\nQuestão: {questao}\n\nImagens: {imagens}\n\nAlternativas: {alternativas}\n\nSe já houver a alternativa correta, apenas explique a resposta com base nas informações fornecidas, caso contrário, resolva a questão e forneça a alternativa correta mencionando na explicação no exato padrão: ...'alternativa correta é b.'... ou ...'alternativa correta é c.'... e assim por diante. Além disso, tudo que puder, deixe no padrão matemático, por exemplo, caso encontre 'y é igual a 250 vezes x', converta para 'y = 250*x', o mesmo para logs, raizes, frações e outros simbolos e termos matemáticos"""

            prompt = prompt_template.format(
                titulo=question["titulo"],
                questao=question["questao"],
                imagens=', '.join(question["descricao_figura"]),
                alternativas=', '.join(question["alternativas"])
            )

            chain = LLMChain(
                llm=self.llm,
                prompt=PromptTemplate(
                    input_variables=["titulo", "questao", "descricao_figura", "alternativas"],
                    template=prompt,
                ),
            )

            while True:
                try:
                    response = chain.invoke({
                        "titulo": question["titulo"],
                        "questao": question["questao"],
                        "imagens": question["descricao_figura"],
                        "alternativas": question["alternativas"]
                    })

                    if isinstance(response, str):
                        try:
                            response = ast.literal_eval(response)
                        except (ValueError, SyntaxError) as e:
                            print(f"Erro ao converter a string em dicionário: {e}")
                            continue

                    alternativa_correta = self.extract_correct_alternative(response.get("text", ""))

                    if "text" in response:
                        response["resolucao"] = response.pop("text")
                    
                    if alternativa_correta:
                        response["alternativa_correta"] = alternativa_correta

                    question.update(response)

                    break
                except Exception as e:
                    print(f"Erro ao processar a questão {question['titulo']}: {e}")
                    continue

            print(f"Resposta para {question['titulo']}:")
            pprint(question)

    def extract_correct_alternative(self, text):
        patterns = [
            r'alternativa correta é ([*]*[a-e][*]*)\.',                
            r'alternativa correta é a letra ([*]*[a-e][*]*)\.',        
            r'alternativa correta é "([*]*[a-e][*]*)"',                
            r'a resposta correta é a alternativa ([*]*[a-e][*]*)\.',   
            r'a resposta correta é "([*]*[a-e][*]*)"',                 
            r'a resposta correta é ([*]*[a-e][*]*)',                   
            r'a alternativa correta é a letra ([*]*[a-e][*]*)\.'       
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).replace('*', '').strip()
        
        return None

if __name__ == "__main__":
    llm_learning = LLMlearning('geometria')
    questions = llm_learning.generate_quiz_by_pdf('quiz.pdf')
    llm_learning.send_questions_to_gemini(questions)