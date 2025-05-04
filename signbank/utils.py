from storages.backends.s3 import S3StaticStorage

class StaticFilesStorage(S3StaticStorage):
    location = "static"
