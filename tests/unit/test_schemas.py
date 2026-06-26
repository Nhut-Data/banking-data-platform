"""Unit tests cho Pydantic schemas."""
import pytest
from src.domains.configs import (
    CustomerSchema, AccountSchema, CardSchema,
    LoanSchema, MerchantSchema, BranchSchema,
)
from src.streaming.schemas import TransactionEvent
from datetime import datetime, timezone


class TestCustomerSchema:
    def test_valid(self):
        c = CustomerSchema(customer_id="CUS001", first_name="A", last_name="B")
        assert c.customer_id == "CUS001"

    def test_credit_score_boundary(self):
        CustomerSchema(customer_id="C1", first_name="A", last_name="B", credit_score=300)
        CustomerSchema(customer_id="C1", first_name="A", last_name="B", credit_score=850)

    def test_credit_score_invalid(self):
        with pytest.raises(Exception):
            CustomerSchema(customer_id="C1", first_name="A", last_name="B", credit_score=299)
        with pytest.raises(Exception):
            CustomerSchema(customer_id="C1", first_name="A", last_name="B", credit_score=851)

    def test_optional_fields_none(self):
        c = CustomerSchema(customer_id="C1", first_name="A", last_name="B")
        assert c.city is None
        assert c.credit_score is None


class TestLoanSchema:
    def test_negative_amount_invalid(self):
        with pytest.raises(Exception):
            LoanSchema(loan_id="L1", customer_id="C1", loan_amount=-1000.0)

    def test_zero_amount_invalid(self):
        with pytest.raises(Exception):
            LoanSchema(loan_id="L1", customer_id="C1", loan_amount=0.0)

    def test_valid_loan(self):
        loan = LoanSchema(
            loan_id="L1", customer_id="C1",
            loan_amount=50000.0, interest_rate=5.5
        )
        assert loan.loan_amount == 50000.0


class TestTransactionEvent:
    def test_valid(self):
        t = TransactionEvent(
            transaction_id="TXN001",
            account_id="ACC001",
            merchant_id="MER001",
            amount_usd=100.0,
            transaction_date=datetime.now(timezone.utc),
        )
        assert t.transaction_id == "TXN001"

    def test_negative_amount_invalid(self):
        with pytest.raises(Exception):
            TransactionEvent(
                transaction_id="TXN001",
                account_id="ACC001",
                merchant_id="MER001",
                amount_usd=-50.0,
                transaction_date=datetime.now(timezone.utc),
            )

    def test_json_roundtrip(self):
        t = TransactionEvent(
            transaction_id="TXN001",
            account_id="ACC001",
            merchant_id="MER001",
            amount_usd=100.0,
            transaction_date=datetime.now(timezone.utc),
        )
        json_str = t.to_json()
        t2 = TransactionEvent.from_json(json_str)
        assert t2.transaction_id == t.transaction_id
        assert t2.amount_usd == t.amount_usd