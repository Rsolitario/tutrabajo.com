import firebase_admin
from firebase_admin import credentials
from firebase_admin import storage

cred = credentials.Certificate('core/apifirebase/config/credenciales.json')
firebase_admin.initialize_app(cred, {
    'storageBucket': 'maki-a30ea.appspot.com'
})

class Bucket(object):

    _instance = None

    def __init__ (self):
        self.bucket = storage.bucket()

    # singleton
    def __new__(cls):
        if Bucket._instance is None:
            Bucket._instance = object.__new__(cls)
        return Bucket._instance

    # solución: https://cloud.google.com/appengine/docs/flexible/python/using-cloud-storage?hl=es_419
    def upload_from_string(self, name, stream) -> {}:
        blob = self.bucket.blob(name)
        try:
            blob.upload_from_string(
                stream.read(),
                stream.content_type
            )
            blob.make_public()
            return {'public_url': blob.public_url}
        except:
            return {'public_url': None}

    def upload_from_filename(self, name, path) -> {}:
        blob = self.bucket.blob(name)
        blob.upload_from_filename(path)
        blob.make_public() # lo configuramos como publico
        return {'public_url' : blob.public_url}

    def download_to_filename(self, name, path) -> None:
        blob = self.bucket.blob(path)
        blob.download_to_filename(name)

    def delete(self, name)-> None:
        blob = self.bucket.blob(name)
        blob.delete()