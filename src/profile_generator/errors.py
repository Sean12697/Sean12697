class SourceError(Exception):
    """Raised by a source when it cannot produce data this run."""


class TemplateError(Exception):
    """Raised when the template references something the context does not have."""
