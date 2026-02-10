"""Tests for admin_telegram_ids parsing in configuration."""

import pytest

from app.config import Settings


def test_parse_admin_ids_csv():
    assert Settings.parse_admin_ids("123, 456,789") == [123, 456, 789]


def test_parse_admin_ids_json_array():
    assert Settings.parse_admin_ids("[123, 456, 789]") == [123, 456, 789]


def test_parse_admin_ids_empty_string():
    assert Settings.parse_admin_ids("") == []


def test_parse_admin_ids_none():
    assert Settings.parse_admin_ids(None) == []
