def setup():
    from rag import LLMlearning
    
    geometria = LLMlearning('geometria')
    models = {'geometria': geometria}
    return models