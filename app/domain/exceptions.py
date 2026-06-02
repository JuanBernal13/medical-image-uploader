class DomainException(Exception):
    pass

class ImageNotFoundError(DomainException):
    def __init__(self, image_id: str):
        self.image_id = image_id
        super().__init__(f"Medical image with ID '{image_id}' not found.")

class ReviewNotFoundError(DomainException):
    def __init__(self, review_id: str):
        self.review_id = review_id
        super().__init__(f"Review with ID '{review_id}' not found.")

class InvalidImageError(DomainException):
    pass

class DatabaseException(DomainException):
    pass
