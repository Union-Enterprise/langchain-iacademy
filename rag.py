import os
import re
import fitz
from pymongo import MongoClient
from dotenv import load_dotenv
from pprint import pprint

load_dotenv()

class LLMlearning:
    def __init__(self, context):
        self.context = context

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
                    "descricao_alternativas": "",
                    "questao": "",
                    "imagens": [],
                    "alternativas": []
                }

            if current_question:
                current_question["questao"] += f" {page_text}"

            descriptions = re.findall(description_pattern, page_text, re.DOTALL) #ta aq o cu do problema esssa porra nao vai ela ta tentando catar descrição na msm pagina do pdf soq esse cu nao consegue catar em outras paginas ele nao identifica regex testado pagina por pagina nao texto corrido tentar separar todas as descriçoes antes dessa bosta rodar dai eu ja vou ter tudo separad o em texto corrido desse diabo de função do cacete eu to ficando maluco alguem me ajuda dessa bosta de tcc estou sentindo minhas forças indo embora. grato

            if descriptions and current_question:
                for description in descriptions:
                    cleaned_description = self.clean_text(description)
                    if "alternativas" in cleaned_description:
                        current_question["descricao_alternativas"] = cleaned_description
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

if __name__ == '__main__':
    geometria = LLMlearning('geometria')
    quiz = geometria.generate_quiz_by_pdf("quiz.pdf")

    pprint(quiz)
