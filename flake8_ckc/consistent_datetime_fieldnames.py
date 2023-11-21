import ast


class DjangoConsistentDatetimeFieldnames(ast.NodeVisitor):

    def __init__(self):
        super().__init__()
        self.errors = []

    def visit_ClassDef(self, node):
        # Check if the class is likely a Django model
        for base in node.bases:
            if isinstance(base, ast.Name) and base.id == 'models.Model':
                self.check_fields(node)
            elif isinstance(base, ast.Attribute) and base.attr == 'Model':
                # Handle cases like django.db.models.Model
                value = base.value
                if isinstance(value, ast.Name) and value.id in {'models', 'django.db.models'}:
                    self.check_fields(node)

    def check_fields(self, node):
        """Check the fields on the django model found in visit_ClassDef"""
        for field in node.body:
            # Inspect field assignments
            if isinstance(field, ast.Assign):
                for target in field.targets:
                    if isinstance(target, ast.Name) and target.id not in {'created_at', 'updated_at'}:
                        # Report an error if the field name doesn't match the convention
                        self.errors.append((
                            target.lineno,
                            target.col_offset,
                            f'CKC001 Field name "{target.id}" does not follow convention.',
                            type(self)
                        ))


class Linter:
    name = 'django-consistent-datetime-field-names'

    def __init__(self, tree: ast.AST):
        self._tree = tree

    def run(self):
        """
        Run the plugin.

        Yields four-element tuples, consisting of:

        #. The line number of the error.
        #. The column offset of the error.
        #. The error message.
        #. The class of the plugin raising the error.
        """

        visitor = DjangoConsistentDatetimeFieldnames()
        visitor.visit(self._tree)

        for error in visitor.errors:
            yield error
