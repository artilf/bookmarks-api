import pytest

import show


class TestGetFailedTemplate(object):
    @pytest.mark.parametrize(
        "expected",
        [({"text": open("src/bookmarklet_result/templates/failed.html.j2").read()})],
    )
    def test_normal(self, expected):
        actual = show.get_failed_template()
        assert actual == expected["text"]
