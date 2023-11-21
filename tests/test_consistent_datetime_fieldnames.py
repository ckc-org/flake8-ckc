from textwrap import dedent

from flake8_ckc.consistent_datetime_fieldnames import Linter

import ast


def test_linter_raises_error_when_datetime_field_doenst_match_convention():
    data = dedent("""
        from django.db import models
        
        class Model(models.Model):
            created_at = models.DateTimeField()
    """)
    tree = ast.parse(data)
    checker = Linter(tree)
    results = list(checker.run())
    # No errors found!
    assert len(results) == 0

    data = dedent("""
        from django.db import models

        class Model(models.Model):
            date_created = models.DateTimeField()
    """)
    tree = ast.parse(data)
    checker = Linter(tree)
    results = list(checker.run())
    # No errors found!
    assert len(results) == 0

    for lineno, col_offset, msg, instance in results:
        assert msg.startswith(
            'CKC001 Field name "date_created" does not follow convention.',
        )