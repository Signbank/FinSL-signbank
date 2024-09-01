from storages.backends.s3 import S3Storage

class StaticFilesStorage(S3Storage):
    location = "static"