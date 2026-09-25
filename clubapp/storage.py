import os

from cloudinary_storage.storage import (
    MediaCloudinaryStorage,
    VideoMediaCloudinaryStorage,
)


class GalleryMediaCloudinaryStorage(MediaCloudinaryStorage):

    def _get_resource_type(self, name):
        extension = os.path.splitext(name)[1].lower()

        video_extensions = [".mp4", ".webm", ".mov"]

        if extension in video_extensions:
            return "video"

        return "image"