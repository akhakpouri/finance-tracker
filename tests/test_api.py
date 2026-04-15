from unittest import TestCase

from fastapi.testclient import TestClient

from app.main import app, store


class FinanceTrackerApiTests(TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)
        store._transactions.clear()  # noqa: SLF001

    def test_health_endpoint(self) -> None:
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})

    def test_create_and_summary_flow(self) -> None:
        expense_response = self.client.post(
            "/api/v1/transactions",
            json={
                "description": "Groceries",
                "amount": "42.50",
                "type": "expense",
                "category": "Food",
                "date": "2026-01-10",
            },
        )
        self.assertEqual(expense_response.status_code, 201)

        income_response = self.client.post(
            "/api/v1/transactions",
            json={
                "description": "Salary",
                "amount": "2000.00",
                "type": "income",
                "category": "Job",
                "date": "2026-01-01",
            },
        )
        self.assertEqual(income_response.status_code, 201)

        summary_response = self.client.get("/api/v1/transactions/summary/overview")
        self.assertEqual(summary_response.status_code, 200)
        self.assertEqual(
            summary_response.json(),
            {"income": "2000.00", "expense": "42.50", "balance": "1957.50"},
        )

    def test_returns_404_for_missing_transaction(self) -> None:
        response = self.client.get("/api/v1/transactions/00000000-0000-0000-0000-000000000000")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"detail": "Transaction not found"})
