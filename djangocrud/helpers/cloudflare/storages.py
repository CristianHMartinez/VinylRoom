from storages.backends.s3 import S3Storage

#static files storage
class StaticFileStorage(S3Storage):
    location = "static"

# media files storage
class MediaFileStorage(S3Storage):
    location = "media"