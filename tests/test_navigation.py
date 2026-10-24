"""Tests for route definitions without starting the graphical application."""

from app.ui.navigation import Routes


def test_mvp_routes_are_unique_and_stable():
    routes = (
        Routes.LOGIN,
        Routes.RECOVERY,
        Routes.NEW_MASTER,
        Routes.VAULT,
        Routes.ENTRY,
        Routes.DETAIL,
        Routes.GENERATOR,
    )

    assert len(routes) == len(set(routes))
    assert routes[0] == "login"
    assert routes[-1] == "generator"
