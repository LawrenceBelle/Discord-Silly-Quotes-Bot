
# For most errors associated with grabbing the quote and the requests to the template website
class QuoteError(Exception):
    pass

# For errors associated with the template text file
class TemplateError(Exception):
    pass

# For errors associated with the author names text file
class AuthorError(Exception):
    pass