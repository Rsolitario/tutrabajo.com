import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

# dos problemas por corregir 1. el path de credenciales no es dinamico
# por lo que se debe fijar dependiendo de donde se llame
# 2. initialize_app tiene nombre por lo que se debe llamar a otra instancia
# anonima para que funcionen.
cred = credentials.Certificate('core/apifirebase/config/credenciales.json')
firebase_admin.initialize_app(cred, name='Database')

class Firestore(object):

    _instance = None

    def __init__(self):
        self.db = firestore.client()
    
    #   singleton
    def __new__(cls):
        if Firestore._instance is None:
            Firestore._instance = object.__new__(cls)
        return Firestore._instance

    def escribir(self, collection:str, document:str, datos:dict) -> None:
        ref = self.db.collection(collection).document(document)
        ref.set(datos)

    # falta agregar id en la collection
    def escribirAdd(self, document, collection, data) -> None:
        doc = self.db.document(document).collection(collection)
        doc.add(data)

    # Obtén todos los documentos de una colección
    def leer(self, collection) -> dict:
        rslt = {}
        users_ref = self.db.collection(collection)
        docs = users_ref.stream()
        
        for doc in docs:
            rslt[doc.id] = doc.to_dict()
        return rslt

    def update_field_doc(self, collection, document, data):
        self.db.collection(collection)  \
               .document(document)      \
               .update(data) 
    
    
    # Advertencia: Si borras un documento, no se borrarán las subcolecciones que contiene.
    def deleteDocument(self, collection, document) -> None:
        self.db.collection(
            collection).document(
                document).delete()     

    # borrar campos
    def deleteField(self, collection, document, field) -> None:
        self.db.collection(collection).document(document).update({field:firestore.DELETE_FIELD})

        '''
        consulta
        < menor que
        <= menor o igual que
        == igual que
        > mayor que
        >= mayor que o igual que
        != no igual a
        array_contains
        array_contains_any
        in
        not-in
        '''

    def consulta(self, collection, key, operador, value, document= '', collection_two = '', limit='', order = '') -> dict:
        rslt = {}
        if document == '' and collection_two =='':
            if limit != '' and order != '':
                docs = self.db.collection(collection).where(key, operador, value).order_by(order).limit(limit).stream() # requiere un index
            elif limit != '' and order == '':
                docs = self.db.collection(collection).where(key, operador, value).limit(limit).stream()
            else:
                docs = self.db.collection(collection).where(key, operador, value).stream()
            for doc in docs:
                rslt[doc.id] = doc.to_dict()
            return rslt
        else:
            if limit != '' and order != '':
                docs = self.db.collection(collection)      \
                .document(document)                         \
                .collection(collection_two)                  \
                .where(key, operador, u''+ value)             \
                .order_by(order).limit(limit).stream()
            elif limit != '' and order == '':
                docs = self.db.collection(collection)   \
                .document(document)                     \
                .collection(collection_two)             \
                .where(key, operador, value).limit(limit).stream()
            else:
                docs = self.db.collection(collection)   \
                .document(document)                     \
                .collection(collection_two)             \
                .where(u'' + key, u'' + operador, u'' + value).stream()
            for doc in docs:
                rslt[doc.id] = doc.to_dict()
            return rslt

    
    def leer_document(self, collection, document) -> dict: # unico valor
        try:
            doc_ref = self.db.collection(collection).document(document)
            doc = doc_ref.get()
            if doc.exists:
                return doc.to_dict()
            else:
                return {}
        except:
            return {}

    # Obtén varios documentos de un grupo de colecciones
    def listCollections(self, collection, document) -> dict: 
        rslt = {}
        collections = self.db.collection(collection).document(document).collections()
        for collection in collections:
            for doc in collection.stream():
                rslt[doc.id] = doc.to_dict()
        return rslt

    def writeCollections(self, collection, document, collection1, document1='', data='') -> None: # leer colección de primer orden
        if document1=='':
            doc_ref = self.db.collection(collection).document(document).collection(collection1)
            doc_ref.add(data)
        else:
            doc_ref = self.db.collection(collection).document(document).collection(collection1).document(document1)
            doc_ref.set(data)

    def deleteDocumentinCollections(self, collection, documente, collection1, document1):
        self.db.collection(collection).document(documente).collection(collection1).document(document1).delete()
    
    def updateCollections(self, collection, document, collection1, document1, data):
        doc_ref = self.db.collection(collection).document(document).collection(collection1).document(document1)
        doc_ref.update(data)

        # escritura de tercer nivel
    def write_collections_3(self,
                            collection,
                            document,
                            collection1,
                            documention1,
                            collection2,
                            documention2,
                            data):
        doc_ref = self.db.collection(collection).document(document) \
            .collection(collection1).document(documention1)         \
            .collection(collection2).document(documention2).set(data)