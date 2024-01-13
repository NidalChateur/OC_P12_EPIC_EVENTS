from epic_events.models.str_template import no, unfilled, yes


class TestTStrTemplate:
    def test_str_template(self):
        assert unfilled == "(Non renseigné)"
        assert yes == "Oui ✅"
        assert no == "Non ❌"
