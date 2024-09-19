import os
import re
import fitz
from pymongo import MongoClient
from dotenv import load_dotenv
from pprint import pprint

load_dotenv()

class LLMlearning:
    def __init__(self, context):
        from vectordb import pdf_to_retriver, txt_to_retriver
        from os import path

        self.context = context

        if path.isfile(f'contexts/{self.context}.txt'):
            self.retriver = txt_to_retriver(self.context)
        else:
            self.retriver = pdf_to_retriver(self.context)

    def connect_to_mongodb(self):
        client = MongoClient(os.environ.get("CONNECTION_STRING"))
        db = client['iacademy']
        return db

    def extract_text_from_pdf(self, pdf_path):
        doc = fitz.open(pdf_path)
        text = ""
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text += page.get_text()
        return text

    def clean_text(self, text):
        return re.sub(r'\s+', ' ', text).strip()

    def extract_images_from_pdf(self, pdf_path, save_dir='images'):
        """
        Extrai e salva todas as imagens do PDF no diretório especificado.
        """
        doc = fitz.open(pdf_path)
        os.makedirs(save_dir, exist_ok=True)
        image_paths = []
        
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            image_list = page.get_images(full=True)
            
            for img_index, img in enumerate(image_list):
                xref = img[0]
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                image_ext = base_image["ext"]
                image_path = os.path.join(save_dir, f"image_{page_num}_{img_index}.{image_ext}")
                
                with open(image_path, "wb") as img_file:
                    img_file.write(image_bytes)
                
                image_paths.append(image_path)
        
        return image_paths

    def extract_questions_from_text(self, text, image_paths):
        question_pattern = r"(QUESTÃO\s+\d+)"
        alternatives_pattern = r"\b([a-eA-E])\.\s+"
        description_pattern = r"(Descrição (?:da|do) (?:figura|gráfico|mapa|quadrinho|imagem|quadro|esquema|alternativas|foto|tabela):.*?\(Fim da descrição\))"
        
        questions_split = re.split(question_pattern, text)

        all_questions = []
        for i in range(1, len(questions_split), 2):
            question_title = f"Questão {questions_split[i].strip()}"
            question_body = questions_split[i + 1].strip()

            description_match = re.search(description_pattern, question_body, re.DOTALL)
            if description_match:
                description = description_match.group(0).strip() 
                
                question_body = question_body.replace(description, "[Imagem: image_placeholder]").strip()
                description = self.clean_text(description) 
                
                if image_paths:
                    image_path = image_paths[0]
                    question_body = question_body.replace("[Imagem: image_placeholder]", f"[Imagem: {image_path}]")
                    image_paths.pop(0)  
                else:
                    image_path = None
            else:
                description = None
                image_path = None

            alternatives_split = re.split(alternatives_pattern, question_body)
            question_text = alternatives_split[0].strip()
            question_text = self.clean_text(question_text) 

            alternatives = []
            for j in range(1, len(alternatives_split) - 1, 2):
                alternative_letter = alternatives_split[j]
                alternative_text = alternatives_split[j + 1].strip()
                alternative_text = self.clean_text(alternative_text)  
                alternatives.append(f"{alternative_letter}. {alternative_text}")

            question_data = {
                "titulo": question_title,
                "questao": question_text,
                "descricao_figura": description,
                "imagem": image_path,
                "alternativas": alternatives
            }
            all_questions.append(question_data)

        return all_questions

    def generate_quiz_by_pdf(self, pdf_path):
        text = self.extract_text_from_pdf(pdf_path)
        image_paths = self.extract_images_from_pdf(pdf_path)
        questions = self.extract_questions_from_text(text, image_paths)
        return questions

if __name__ == '__main__':
    geometria = LLMlearning('geometria')
    quiz = geometria.generate_quiz_by_pdf("quiz.pdf")

    pprint(quiz[0])
