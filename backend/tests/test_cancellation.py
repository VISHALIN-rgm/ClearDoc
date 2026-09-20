import cancellation


def test_request_and_check_cancel():
    cancellation.clear("doc-1")  # ensure clean state

    assert cancellation.is_cancelled("doc-1") is False

    cancellation.request_cancel("doc-1")
    assert cancellation.is_cancelled("doc-1") is True

    cancellation.clear("doc-1")
    assert cancellation.is_cancelled("doc-1") is False


def test_clear_on_unflagged_id_is_a_noop():
    cancellation.clear("never-flagged")  # should not raise
    assert cancellation.is_cancelled("never-flagged") is False


def test_cancel_ids_are_independent():
    cancellation.request_cancel("doc-a")
    assert cancellation.is_cancelled("doc-b") is False
    cancellation.clear("doc-a")
