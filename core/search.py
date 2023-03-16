import re
import spacy
import sklearn
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
# Tal y como indica la documentación de Spanish - spaCy, debes bajarte los modelos:

# python -m spacy download es_core_news_sm
# en = en_core_web_sm

# Motor de busqueda con spacy. Tutorial: https://www.youtube.com/watch?v=-jx042EwCWU

class Search:
    pln = spacy.load('es_core_news_sm', disable=["tagger", "parse", "ner"]) # es: es_core_news_sm

    def __init__(self, doclist:list, content:str | None = None) -> None:
        self.doc = doclist
        self.content = content
    # Pre-procesamiento(spacy)
    # -tokenización
    # -eliminar 'stop words' {'un}, 'y', 'pero'}
    # -lematización (perros... perro, corriendo... correr)
    # -eliminar todo lo que contenga caracteres no alfabeticos
    def preprocess(self, text):
        r:list = []
        doc = self.pln(text)
        for token in doc:
            if not (token.is_stop) and (token.is_alpha):
                r.append(token.lemma_)
        return r
    #print(preprocess(doc[0]))
    # Vectorizacion (sklearn)
    # pasar el texto a una matriz de coincidencia de palabras
    # las columnas representan palabras del diccionario
    def search(self, termino_de_busqueda):
        vec = TfidfVectorizer(tokenizer=self.preprocess)
        X = vec.fit_transform(self.doc)
        # guardamos los indices con idf de bajo a alto
        # mientras mas alto el idf su frecuencia de uso es menor 
        ordenadoidf = np.argsort(vec.idf_) 
        columnas = np.array(vec.get_feature_names_out())
        terminos = columnas[ordenadoidf]

        # El motor de busqueda
        from sklearn.neighbors import NearestNeighbors
        neigh = NearestNeighbors(n_neighbors=2)
        neigh.fit(X)
        consulta = vec.transform([termino_de_busqueda])
        indices = neigh.kneighbors(consulta, return_distance=False).squeeze()
        return list(map(lambda x: self.doc[x], indices))
    
    def show(self):
        if type(self.doc) == list:
            return self.doc
        else:
            return self.content

    def underline(self, find:str, end:str='\n'):
        s = re.search(find.lower(), self.content)
        try:
            content_find = self.content[s.start():]
        except AttributeError:
            print("No se encontro la cade")
            exit()
        e = re.search(end, content_find)
        return content_find[:e.start()]


    