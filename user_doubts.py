from rag import rag
from ia_model import llm

def user_doubt(input, context, previous={"question": None, "response": None}):
    is_valid_question = llm.invoke(f'isto é uma pergunta acadêmica sobre matemática? responda apenas com as palavras "True" ou "False", apenas com a primeira letra em maiúsculo e sem pontuações. Responda "True" também se a pergunta fizer sentido no seguinte contexto: Contexto: {previous['response']} Pergunta: {input}').content
    if is_valid_question[0] == "T":
        return rag(input, context=context, question_context=previous)
    else:
        return "Por favor, pergunte algo pertinente ao conteúdo."

if __name__ == '__main__':
    print(user_doubt("pode me explicar novamente o passo tres?", 'geometria',
                     previous={"question": "como calcular a area de um circulo", 
                      "response": "A área de um círculo é calculada utilizando a seguinte fórmula:**Área = π * r²**Onde:* **π (pi)** é uma constante matemática que representa a razão entre a circunferência de um círculo e seu diâmetro, aproximadamente igual a 3,14159.* **r** é o raio do círculo, que é a distância do centro do círculo até qualquer ponto na sua circunferência.**Exemplo:**Vamos calcular a área de um círculo com raio de 5 cm:1. **Substitua o valor do raio na fórmula:** Área = π * (5 cm)²2. **Calcule o quadrado do raio:** Área = π * 25 cm²3. **Multiplique o resultado por π:** Área ≈ 3,14159 * 25 cm² ≈ 78,54 cm²Portanto, a área do círculo com raio de 5 cm é aproximadamente 78,54 cm²."}))
    
