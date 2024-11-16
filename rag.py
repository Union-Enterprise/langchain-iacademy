import os
import re
import fitz
from pymongo import MongoClient
from dotenv import load_dotenv
from pprint import pprint
from langchain import LLMChain
from langchain.prompts import PromptTemplate
import ast
import json
from bson import ObjectId
import requests

from langchain_core.prompts import ChatPromptTemplate
from defaults_prompts import content, roadmap, question_template, gen_quiz
from ia_model import llm

load_dotenv()

class LLMlearning:
    def __init__(self):
        self.llm = llm
        self.simple_roadmap = {}
        
    def connect_to_mongodb(self):
        client = MongoClient(os.environ.get("CONNECTION_STRING"))
        db = client['iacademy'] 
        return db
    
    def generate_roadmap(self, id):
        prompt = PromptTemplate(template=roadmap, input_variables=[])
        chain = LLMChain(llm=llm, prompt=prompt)

        while True:
            while True:
                try:
                    content = chain.invoke({})
                    break
                except:
                    continue
            try:
                json_object = json.loads(content['text'].replace("```", "").replace("json", "").replace('\n', ''))
                break
            except Exception as err:
                print(err)
                print("ia ta moscano e n ta mandando o roadmap em json mas vai gerar dnv rlx")
                json_object = {}
                continue
        
        self.roadmap = json_object
        # self.simple_roadmap = self.roadmap.keys()
        self.generate_from_roadmap(id)


    def generate_from_roadmap(self, id, prompt=None):
        db = self.connect_to_mongodb()
        user_collection = db["users"]
        
        user_data = user_collection.find_one({"_id": ObjectId(id)})
        quiz_iniciais = user_data.get("quiz_iniciais", "Sem quizzes disponíveis")

        default_local_prompt = prompt if prompt else content

        prompt_chat = ChatPromptTemplate.from_template(
            default_local_prompt + """
            \nPergunta: {input}
            """
        )

        for topic in list(self.roadmap.keys()):
            pprint(self.roadmap[topic])
            for cu in list(self.roadmap[topic]['unidades'].keys()):
                for subject in list(self.roadmap[topic]['unidades'][cu]['topicos'].keys()):
                    print("- "+subject+f" ({self.roadmap[topic]['unidades'][cu]['title']})")
                    try:
                        self.simple_roadmap[self.roadmap[topic]['unidades'][cu]["title"]].append(subject)
                    except:
                        self.simple_roadmap[self.roadmap[topic]['unidades'][cu]["title"]] = [subject]

                    formatted_prompt = prompt_chat.format(quizzes=quiz_iniciais, input=f"gere tudo sobre {subject} - {topic} para a unidade {self.roadmap[topic]['unidades'][cu]['title']}")
                    
                    while True:
                        while True:
                            try:
                                response = llm.invoke(formatted_prompt)
                                break
                            except: 
                                continue
                        try:
                            json_object = json.loads(response.content)
                        except json.JSONDecodeError:
                            print("ia ta moscano e n ta mandando o conteudo em json mas vai gerar dnv rlx")
                            json_object = {}
                            continue

                        try:
                            pprint(json_object)

                            tags = json_object.pop("Tags")
                            titulo = json_object.pop("Titulo")
                            descricao = json_object.pop("Descrição")
                            query = json_object['images_google_search']
                            
                            try:
                                img_tag = f"<img href=\"{self.get_images(query)[0]}\">"
                                json_object['images_google_search'] = img_tag
                            except Exception as err:
                                print(err)
                                pass

                            topic_data = {
                                'title': titulo,
                                'topic': topic,
                                'description': descricao,
                                'content': json_object,
                                'tags': tags,
                                'views': 0
                            }
                            self.roadmap[topic]['unidades'][cu]['topicos'][subject] = topic_data
                            pprint(topic_data)
                            break
                        except Exception as err:
                            print(err)
                            continue

        # conteudos
        update_operation = { "$set" : 
            { "topics" : self.roadmap }
        }
        result = user_collection.update_one({ "_id" : ObjectId(id) }, update_operation)
        if result.matched_count == 0:
            print(f"nenhum usuario com id {id}.")

        #roadmap
        update_operation = { "$set" : 
            { "roadmap" : self.simple_roadmap }
        }
        result = user_collection.update_one({ "_id" : ObjectId(id) }, update_operation)
        if result.matched_count == 0:
            print(f"nenhum usuario com id {id}.")

    
    def extract_text_from_pdf(self, pdf_path):
        doc = fitz.open(pdf_path)
        text = ""
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text += page.get_text() + "\n"
        return text

    def clean_text(self, text):
        return re.sub(r'\s+', ' ', text).strip()
    
    def get_images(self, query):
        cse_id = os.environ.get("CSE_ID")
        api_key = os.environ.get("CUSTOM_SEARCH_API_KEY")
        num=1

        url = f"https://www.googleapis.com/customsearch/v1?q={query}&searchType=image&key={api_key}&cx={cse_id}&num={num}"
        response = requests.get(url)
        data = response.json()
        
        images = []
        
        if 'items' in data:
            for item in data['items']:
                images.append(item['link'])

        return images

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
        for i, description in enumerate(descriptions):
            imagem_path = imagens[i] if i < len(imagens) else None
            if imagem_path:
                imagem_tag = f"\n<img src=\"http://localhost:5000/{imagem_path}>\">\n"
                page_text = page_text.replace(description, imagem_tag)
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
                    "description_figura": [],
                    "alternativa_description": "",
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
                        current_question["alternativa_description"] = cleaned_description
                    else:
                        current_question["description_figura"].append(cleaned_description)

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
                for i in range(len(current_question["description_figura"])):
                    if i < len(current_question["imagens"]):
                        imagem_tag = f"<imagem {current_question['imagens'][i]}>"
                        current_question["questao"] = current_question["questao"].replace(current_question["description_figura"][i], imagem_tag)

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
        db = self.connect_to_mongodb()
        topic_collection = db['quizes']
        questions_vector = []
        bglh = list(self.simple_roadmap.values())
        # str_roadmap = json.dumps(self.simple_roadmap, ensure_ascii=False).replace("{", "{{").replace("}", "}}")
        # print(str_roadmap)
        for question in questions:
            # print(bglh)
            prompt = question_template.format(
                titulo=question["titulo"],
                questao=question["questao"],
                imagens=', '.join(question["description_figura"]),
                alternativas=', '.join(question["alternativas"]),
                roadmap=bglh
            )

            chain = LLMChain(
                llm=self.llm,
                prompt=PromptTemplate(
                    input_variables=["titulo", "questao", "description_figura", "alternativas", "roadmap"],
                    template=prompt,
                ),
            )

            while True:
                try:
                    response = chain.invoke({
                        "titulo": question["titulo"],
                        "questao": question["questao"],
                        "imagens": question["description_figura"],
                        "alternativas": question["alternativas"],
                        "roadmap": bglh
                    })

                    if isinstance(response, str):
                        try:
                            response = ast.literal_eval(response["resolucao"])
                        except (ValueError, SyntaxError) as e:
                            print(f"Erro ao converter a string em dicionário: {e}")
                            continue

                    alternativa_correta = self.extract_correct_alternative(response.get("text", ""))

                    if "text" in response:
                        response["resolucao"] = response.pop("text")
                    
                    if alternativa_correta:
                        response["alternativa_correta"] = alternativa_correta
                    # else:
                    #     alternativa_correta = response['alternativa_correta']

                    string_json = ' '.join(response['resolucao'].replace('```python\n', '').replace('```', '').replace(',\n', ',').replace("\\", "\\\\").replace('json', "").replace("\\\"", "\"").split())
                    
                    questao_dict = json.loads(string_json)

                    data = {
                        'titulo': response['titulo'],
                        'questao': questao_dict['questao'],
                        'explicacao': questao_dict['explicacao'],
                        'alternativa_correta': questao_dict['alternativa_correta'],
                        'alternativas': response['alternativas'],
                        'imagens': question['imagens'],
                        'descricao_figuras': response['imagens'],
                        'tema': questao_dict['tema']
                    }

                    question.update(data)
                    questions_vector.append(data)

                    topic_collection.insert_one(data)
                    break
                except Exception as e:
                    # print(questao_dict)
                    print(f"Erro ao processar a questão {question['titulo']}: {e}")
                    continue
        
        return questions_vector

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


    def user_doubt_content(self, user_prompt, content, chat_history):
        from defaults_prompts import user_doubt_prompt

        prompt_chat = ChatPromptTemplate.from_template(user_doubt_prompt)

        formatted_prompt = prompt_chat.format(prompt=user_prompt, content=content, history=chat_history)

        print(formatted_prompt)

        response = llm.invoke(formatted_prompt)

        return response.content
    
    def gen_quiz(self, qtd, tema):
        prompt = gen_quiz.format(
            quantidade=qtd,
            tema=tema
        )

        chain = LLMChain(
            llm=self.llm,
            prompt=PromptTemplate(
                input_variables=["quantidade", "tema"],
                template=prompt
            ),
        )

        while True:
            try:
                response = chain.invoke({
                    "quantidade": qtd,
                    "tema": tema,
                })

                json_object = json.loads(response['text'].replace("```", "").replace("json", "").replace('\n', ''))
                break
            except Exception as err:
                print(err)
                print("ia n ta gerando os quiz em json, mas vai gerar dnv rlx")
                json_object = {}
                continue

        db = self.connect_to_mongodb()
        quizes_collection = db["quizes"]

        quizes_collection.insert_many(json_object)
        return json_object


if __name__ == "__main__":
    llm_learning = LLMlearning()


    llm_learning.gen_quiz("10", "algebra")


    # pprint(llm_learning.roadmap)
    # pprint('---')
    # pprint(llm_learning.simple_roadmap)

    # print(json.dumps({"chave": {"name": "bruno"}, "chave6": {"name6": "bruno6"}}).replace("{", "{{").replace("}", "}}"))