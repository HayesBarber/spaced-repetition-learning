from srl.utils import _score, fuzzy_find


def test_score_exact_match():
    score = _score("abc", "abc")
    assert score is not None


def test_score_sequential_chars():
    score = _score("ts", "two-sum")
    assert score is not None
    assert score > 0


def test_score_no_match():
    assert _score("xyz", "abc") is None


def test_score_not_all_chars_found():
    assert _score("abcd", "abc") is None


def test_score_empty_query():
    score = _score("", "anything")
    assert score is not None


def test_score_word_boundary_bonus():
    boundary = _score("ts", "two-sum")
    no_boundary = _score("ts", "xxts")
    assert boundary > no_boundary


def test_fuzzy_find_filters_by_query():
    data = [{"name": "two-sum"}, {"name": "three-sum"}, {"name": "other"}]
    result = fuzzy_find("sum", data, lambda x: x["name"])
    assert len(result) == 2
    names = {r["name"] for r in result}
    assert names == {"two-sum", "three-sum"}


def test_fuzzy_find_no_matches():
    result = fuzzy_find("xyz", [{"name": "abc"}], lambda x: x["name"])
    assert result == []


def test_fuzzy_find_skips_none_extractor():
    data = [{"name": "abc"}, {"name": None}]
    result = fuzzy_find("abc", data, lambda x: x.get("name"))
    assert len(result) == 1


def test_fuzzy_find_case_insensitive():
    data = [{"name": "Two-Sum"}, {"name": "other"}]
    result = fuzzy_find("two", data, lambda x: x["name"])
    assert len(result) == 1
    assert result[0]["name"] == "Two-Sum"


def test_fuzzy_find_sorts_by_score():
    data = [{"name": "aatest"}, {"name": "test"}]
    result = fuzzy_find("test", data, lambda x: x["name"])
    assert len(result) == 2
    assert result[0]["name"] == "test"
