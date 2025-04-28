from storages.backends.s3 import S3Storage

#static files storage
class StaticFileStorage(S3Storage):
    helpers.cloudflare.storages.StaticFileStorage
    locarion = "static"

# media files storage
class MediaFileStorage(S3Storage):
    # helpers.cloudflare.storages.MediaFileStorage
    location = "media"