from srl.utils import fuzzy_find


def test_match():
    results = fuzzy_find(
        "tws",
        [
            "two-sum",
            "three-sum",
        ],
    )

    assert [p for _, p in results] == [
        "two-sum",
    ]


def test_exact_match():
    results = fuzzy_find(
        "two-sum",
        [
            "two-sum",
            "three-sum",
        ],
    )

    assert results[0][1] == "two-sum"


def test_non_matching_candidates_are_filtered():
    results = fuzzy_find(
        "tws",
        [
            "two-sum",
            "three-sum",
            "add-two-numbers",
        ],
    )

    assert [p for _, p in results] == [
        "two-sum",
        "add-two-numbers",
    ]


def test_no_match():
    results = fuzzy_find(
        "xyz",
        [
            "two-sum",
            "three-sum",
        ],
    )

    assert results == []


def test_case_insensitive():
    results = fuzzy_find(
        "TWS",
        [
            "Two-Sum",
        ],
    )

    assert len(results) == 1
    assert results[0][1] == "Two-Sum"


def test_dash_bonus_wins():
    results = fuzzy_find(
        "sum",
        [
            "sum-of-two-integers",
            "two-sum",
        ],
    )

    assert results[0][1] == "two-sum"


def test_shorter_candidate_wins_tie():
    results = fuzzy_find(
        "ab",
        [
            "ab",
            "alphabet",
        ],
    )

    assert results[0][1] == "ab"


def test_empty_query_matches_everything():
    results = fuzzy_find(
        "",
        [
            "two-sum",
            "three-sum",
        ],
    )

    assert len(results) == 2
