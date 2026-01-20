class ContentNeedsReviewError(Exception):
    def __init__(self, message="Content needs review", code="needs_review"):
        self.message = message
        self.code = code
        super().__init__(message)
