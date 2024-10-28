content = """
    Quero que aja como um professor de um adolescente que está estudando para o ENEM, uma prova de vestibular brasileiro.
    Eu irei te enviar apenas o tema (e.g Triângulos na Geometria Plana) e você deve me retornar informações organizadas sobre o assunto, entendido?
    Quero que explique detalhadamente, sem conselhos e modéstias, seja direto ao ponto.
    Não quero um resumo básico, quero que você se aprofunde no tema e cite todos os pontos que conter no contexto.
    Você será o alimentador de um portal de trilhas de conhecimento, onde, cada tópico contém assuntos, por exemplo, dentro de "Geometria Plana", há "Quadrados", "Triângulos", "Trapézios" etc. Logo, não há a necessidade de explicar conceitos como "Teorema de Pitágoras" dentro do assunto "Quadrado", pois ele será abordado no assunto "Triângulos"
    Não aja como uma inteligência artificial, pois, meu usuário não terá acesso à você, então não trate como se, após seu output, o usuário ainda consiga comunicar contigo, pois ele não conseguirá. Por exemplo, sem: "Avise-me se desejar explorar algum aspecto específico com mais detalhes ou se tiver qualquer dúvida!"

    Responda como JSON entre chaves e sem quebra de linha, no seguinte modelo:
        Titulo: "..."
        Tags: ["Geometria espacial", "Formas", ...]
        Definição: "(um texto explicativo)",
        Explicação: "(um texto explicativo)",
        Tópico 1 de explicação: "(um texto explicativo)",
        Tópico 2 de explicação: "(um texto explicativo)",
        ...
        Fórmulas: "(um texto explicativo juntamente com as formulas e o que cada incognita representa)"

    Gere em média umas 5 tags que façam referencia ao conteúdo que você gerar (SEMPRE GERE AS TAGS, Não gere a tag "ENEM" nem "Matemática").
    No JSON não precisa usar "Tópico 1, Tópico 2..." como chaves, utilize o próprio título.
    Em hipótese alguma retorne o JSON entre "``````"
    O número de topicos de explicações pode variar conforme sua necessidade de explicar o tema.
"""

roadmap = """gere um dicionario em python que possua todos os assuntos que caem no enem em matematica, em ordem de dificuldade, ou seja, comece com aritmetica por exemplo, matematica basica e vá evoluindo, por exemplo, no seguinte padrao: (não deixe de gerar tudo dentro da chave "conteudos")
        conteudos: {{
            "geometria plana": {{
                title: "Geometria Plana"
                topics: {{
                    "quadrados": {{(deixe vazio)}},
                    "triangulos": {{(deixe vazio)}}, ...
                }}, (em ordem de dificuldade)
                description: "a geometria plana é um assuntos que aborda as figuras bidimensionais..." (algo entre 10 linhas de conteudo),
                tags: ["Geometria", "Áreas", "Bidimensionais" ... (umas 5 tags ou mais)],
                level: "básico"
            }},
            "geometria espacial": {{
                title: "Geometria Espacial"
                topics: {{
                    "cubos": {{(deixe vazio)}},
                    "piramides": {{(deixe vazio)}},
                    "prismas": {{(deixe vazio)}}...
                }}, (em ordem de dificuldade)
                description: "a geometria espacial é um assuntos que aborda as figuras tridimensionais..." (algo entre 10 linhas de conteudo),
                tags: ["Geometria", "Volumes", "Tridimensionais" ... (umas 5 tags ou mais)],
                level: "intermediário"
            }}
        }}  
        em hipotese alguma envolva sua resposta em "``````". 
        eu quero um json como resposta, ou seja, retire as quebras de linha.
"""

question_template = """{titulo}\n\nQuestão: {questao}\n\nImagens: {imagens}\n\nAlternativas: {alternativas}\n\nSe já houver a alternativa correta, apenas explique a resposta com base nas informações fornecidas, caso contrário, resolva a questão e forneça a alternativa correta mencionando na explicação no exato padrão: ...'alternativa correta é b.'... ou ...'alternativa correta é c.'... e assim por diante. Além disso, tudo que puder, deixe no padrão matemático, por exemplo, caso encontre 'y é igual a 250 vezes x', converta para 'y = 250*x', o mesmo para logs, raizes, frações e outros simbolos e termos matemáticos, converta "por cento" para "%", "metros quadrados" para m², C índice 1 para C₁ etc.
    retorne um dicionario python no seguinte padrao: 

            "questao": "...", (questão corrigida no quesito dos termos matemáticos, eg. 'y é igual a 250 vezes x', converta para 'y = 250*x')

            "descricao_figuras": "..."(aquilo que for descrição das figuras, de "Descrição do gráfico" ou algo do tipo, ate "(Fim da descrição)")
            
            "explicacao": "..."

            "tema": "..." (qual dos seguintes temas a minha questão mais se enquadra? caso entre em mais de um topico, considere o mais dificil entre eles, deixe apenas um, apenas o texto, sem "[]": {roadmap})

            "alternativa_correta": "..." (apenas a letra da alternativa correta)

            de forma alguma deixe a resposta entre "```(resposta)```", sempre insira virgula após cada par de chave e valor.

            caso uma questão nao seja uma pergunta (não terminar com "?"), finalize-a com ":" (ainda dentro da string da questão), para representar uma questão.

            caso tenha alguma descrição de imagem dentro da questão, pode mover para a chave "descricao_figuras".

            não retire a minha tag \n\n<img src=\"http://localhost:5000/images/<any_path>\">\n da minha questão, ela é muito importante
"""