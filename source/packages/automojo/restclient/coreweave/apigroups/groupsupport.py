"""
    .. module:: groupsupport
    :platform: Darwin, Linux, Unix, Windows
    :synopsis: Shared helpers used by the CoreWeave api-group classes —
        JSON decoding and transparent paging-cursor traversal.

    .. moduleauthor:: Myron Walker <myron.walker@gmail.com>
"""

__author__ = "Myron Walker"
__copyright__ = "Copyright 2026, Automation Mojo LLC"
__credits__ = []


from typing import Any, Callable, Dict, List

from requests import Response


def safe_json(*, response: Response) -> Dict[str, Any]:
    """
        Parse a response body as a JSON object, degrading to an empty dict.

        :param response: The :class:`Response` to parse.

        :returns: The decoded object, or an empty dict.
    """
    try:
        payload = response.json()
    except ValueError:
        rtnval: Dict[str, Any] = {}
        return rtnval

    if not isinstance(payload, dict):
        rtnval = {}
        return rtnval

    rtnval = payload
    return rtnval


def collect_paged_items(*, fetch_page: Callable[[Dict[str, str]], Dict[str, Any]],
                        items_key: str = "items") -> List[Dict[str, Any]]:
    """
        Traverse every page of a paged CoreWeave list endpoint and return the
        concatenated union of items.

        The traversal follows the ``next_cursor`` field returned in each page
        payload until the field is absent or empty. The result is a single
        concatenated list, in page order, with no item dropped or duplicated.

        :param fetch_page: A callable that, given a query-parameter dict,
            issues one page request and returns the decoded page payload.
            The first call receives an empty dict; subsequent calls receive
            ``{"cursor": <token>}``.
        :param items_key: The payload key holding the per-page item list.

        :returns: The concatenated list of item dicts across all pages.
    """
    collected: List[Dict[str, Any]] = []
    query_params: Dict[str, str] = {}
    seen_cursors = set()

    while True:
        page = fetch_page(query_params)

        page_items = page.get(items_key, None)
        if page_items is not None:
            for item in page_items:
                collected.append(item)

        next_cursor = page.get("next_cursor", None)

        if next_cursor is None:
            break

        if len(next_cursor) == 0:
            break

        if next_cursor in seen_cursors:
            # Defensive guard against a server returning a cyclic cursor.
            break

        seen_cursors.add(next_cursor)
        query_params = {"cursor": next_cursor}

    rtnval = collected
    return rtnval


__all__ = ["safe_json", "collect_paged_items"]
