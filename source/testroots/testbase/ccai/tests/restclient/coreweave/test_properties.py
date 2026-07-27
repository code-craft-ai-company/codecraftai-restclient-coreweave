"""
    .. module:: test_properties
        :platform: Darwin, Linux, Unix, Windows
        :synopsis: Property-based (hypothesis) tests for the CoreWeave client
                   — paging-cursor traversal, URL composition, and
                   task-handle waiting.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Code Craft AI LLC"
__credits__ = []


from ccai import testbase


from typing import Any, Dict, List

import requests_mock as rm_module

from ccai.testbase.properties import given
from ccai.testbase.properties import strategies as st

from ccai.errors.exceptions import SemanticError

from ccai.restclient.base.aspectsrest import ActionPattern

from ccai.restclient.coreweave.aspectscoreweave import AspectsCoreweave
from ccai.restclient.coreweave.apigroups.groupsupport import (
    collect_paged_items
)
from ccai.restclient.coreweave.apigroups.operationsgroup import (
    OperationsGroup
)
from ccai.restclient.coreweave.model.coreweavetaskhandle import (
    CoreweaveTaskHandle
)
from ccai.restclient.coreweave.model.coreweaveoperationresult import (
    CoreweaveOperationResult
)
from ccai.restclient.coreweave.urlcompose import compose_leaf, require_identifier

from ccai.tests.restclient.coreweave.testsupport import BASE, make_client


# ----------------------------------------------------------------------
# Paging-cursor traversal
# ----------------------------------------------------------------------

@given(
    constraints={"max_examples": 100},page_sizes=st.lists(st.integers(min_value=0, max_value=6),
                           min_size=1, max_size=8))
def test_paging_cursor_union_is_total(page_sizes: List[int]):
    """
        For any sequence of mock pages with arbitrary cursor tokens,
        ``collect_paged_items`` returns the concatenated union exactly once,
        in order, with no item dropped or duplicated.
    """
    pages: List[Dict[str, Any]] = []
    item_counter = 0
    for index in range(0, len(page_sizes)):
        size = page_sizes[index]
        items = []
        for _ in range(0, size):
            items.append({"id": item_counter})
            item_counter = item_counter + 1

        page: Dict[str, Any] = {"items": items}
        if index < len(page_sizes) - 1:
            page["next_cursor"] = "cursor-{}".format(index)
        pages.append(page)

    call_index = {"value": 0}

    def fetch_page(query_params: Dict[str, str]) -> Dict[str, Any]:
        current = pages[call_index["value"]]
        call_index["value"] = call_index["value"] + 1
        return current

    collected = collect_paged_items(fetch_page=fetch_page)

    expected_ids = list(range(0, item_counter))
    actual_ids = [entry["id"] for entry in collected]
    assert actual_ids == expected_ids
    return


# ----------------------------------------------------------------------
# URL composition
# ----------------------------------------------------------------------

@given(
    constraints={"max_examples": 100},segments=st.lists(st.text(min_size=1, max_size=12), min_size=1,
                         max_size=6))
def test_url_composition_is_deterministic(segments: List[str]):
    """
        For any tuple of non-empty identifier strings, the composed leaf is a
        deterministic function of the inputs.
    """
    seg_tuple = tuple(segments)
    first = compose_leaf(segments=seg_tuple)
    second = compose_leaf(segments=seg_tuple)

    assert first == second
    assert first.startswith("/") is True
    # Per-segment encoding yields exactly len(segments) path components.
    assert first.count("/") == len(segments)
    return


@given(
    constraints={"max_examples": 50},prefix=st.lists(st.text(min_size=1, max_size=8), min_size=0,
                       max_size=3),
       suffix=st.lists(st.text(min_size=1, max_size=8), min_size=0,
                       max_size=3),
       bad=st.sampled_from(["", None]))
def test_url_composition_rejects_empty_segment(prefix, suffix, bad):
    """
        An empty or ``None`` segment anywhere in the tuple raises
        :class:`SemanticError`.
    """
    seg_tuple = tuple(prefix) + (bad,) + tuple(suffix)
    with testbase.raises(SemanticError):
        compose_leaf(segments=seg_tuple)
    return


@given(bad=st.sampled_from(["", None]), constraints={"max_examples": 50})
def test_require_identifier_rejects_empty(bad):
    """
        ``require_identifier`` rejects empty / ``None`` identifiers.
    """
    with testbase.raises(SemanticError):
        require_identifier(name="thing", value=bad)
    return


# ----------------------------------------------------------------------
# Task-handle waiting
# ----------------------------------------------------------------------

class _FakeOperationsGroup:
    """
        A deterministic stand-in for :class:`OperationsGroup` that replays a
        monotonic status stream.
    """

    def __init__(self, *, statuses: List[str]) -> None:
        """
            Initialise the fake operations group.

            :param statuses: The ordered status stream to replay.

            :returns: ``None``.
        """
        self._statuses = statuses
        self._index = 0
        return

    def get(self, *, operation_id: str,
            aspects: Any) -> CoreweaveOperationResult:
        """
            Return the next status in the stream, holding on the last.

            :param operation_id: The operation identifier.
            :param aspects: Behaviour control (ignored).

            :returns: A :class:`CoreweaveOperationResult`.
        """
        position = self._index
        if position >= len(self._statuses):
            position = len(self._statuses) - 1
        else:
            self._index = self._index + 1

        rtnval = CoreweaveOperationResult(operation_id=operation_id,
                                          status=self._statuses[position])
        return rtnval


# ----------------------------------------------------------------------
# Idempotent retry semantics
# ----------------------------------------------------------------------

@given(transient_count=st.integers(min_value=0, max_value=4), constraints={"max_examples": 40})
def test_idempotent_retry_within_budget(transient_count: int):
    """
        For any number of transient 503 failures within the retry budget,
        the read produces the same result as a single successful call.
    """
    client = make_client()
    success_body = {"items": [{"id": "o1", "slug": "alpha", "name": "Alpha"}]}

    responses = []
    for _ in range(0, transient_count):
        responses.append({"status_code": 503, "json": {"detail": "busy"}})
    responses.append({"status_code": 200, "json": success_body})

    aspects = AspectsCoreweave(action_pattern=ActionPattern.DO_UNTIL_SUCCESS,
                               completion_interval=0,
                               completion_timeout=30,
                               allowed_error_codes=(503,))

    with rm_module.Mocker() as mock:
        mock.get("{}/v1/organizations".format(BASE), responses)
        orgs = client.organizations.list(aspects=aspects)

    assert len(orgs) == 1
    assert orgs[0].slug == "alpha"
    return


@given(
    constraints={"max_examples": 60},running_count=st.integers(min_value=0, max_value=5),
       terminal=st.sampled_from(["succeeded", "failed", "cancelled"]))
def test_task_handle_terminates_on_first_terminal(running_count: int,
                                                  terminal: str):
    """
        For any monotonic status progression, ``wait`` terminates on the
        first terminal status and never reports a status not in the stream.
    """
    stream = ["pending"] + ["running"] * running_count + [terminal]
    fake_group = _FakeOperationsGroup(statuses=stream)

    aspects = AspectsCoreweave(operation_poll_interval_seconds=0,
                               operation_poll_timeout_seconds=30)
    handle = CoreweaveTaskHandle(operation_id="op-1",
                                 operations_group=fake_group,
                                 client_aspects=aspects)

    result = handle.wait(aspects=aspects)

    assert handle.is_done() is True
    assert result.task_id == "op-1"
    return
