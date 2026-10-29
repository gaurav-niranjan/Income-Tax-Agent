from income_tax_agent.limits import QuestionLimits

HOUR = 3600


def test_visitor_limit_and_window():
    limits = QuestionLimits(per_visitor=2, total=10, window_s=24 * HOUR)
    limits.record("a", now=0)
    limits.record("a", now=HOUR)
    assert limits.left("a", now=2 * HOUR) == (0, 8)
    assert limits.left("b", now=2 * HOUR) == (2, 8)  # other visitors are not affected
    assert limits.free_again_in("a", now=2 * HOUR) == 22 * HOUR
    assert limits.left("a", now=24 * HOUR) == (1, 9)  # the first question has left the window


def test_total_limit_across_visitors():
    limits = QuestionLimits(per_visitor=5, total=2, window_s=24 * HOUR)
    limits.record("a", now=0)
    limits.record("b", now=0)
    assert limits.left("c", now=1) == (5, 0)


def test_free_again_in_without_questions():
    assert QuestionLimits(per_visitor=1, total=1, window_s=HOUR).free_again_in("a") == 0
