import pytest
from datetime import datetime
import sqlite3

from ultimate_mcp_server.modules.data_types import (
    AddPlayerCommand,
    AddFederationPaymentCommand,
    RemoveLastFederationPaymentCommand,
    ListFederationPaymentsCommand
)
from ultimate_mcp_server.modules.functionality.add_player import add_player
from ultimate_mcp_server.modules.functionality.add_federation_payment import add_federation_payment
from ultimate_mcp_server.modules.functionality.remove_last_federation_payment import remove_last_federation_payment
from ultimate_mcp_server.modules.functionality.list_federation_payments import list_federation_payments


@pytest.fixture
def test_player(temp_db_uri):
    """Create a test player."""
    command = AddPlayerCommand(
        name="Test Player",
        phone="123-456-7890",
        email="test@example.com",
        db_uri=temp_db_uri
    )
    return add_player(command)


def test_add_federation_payment(temp_db_uri, test_player):
    """Test adding a federation payment for a player."""
    # Set payment details
    payment_date = datetime.now().replace(microsecond=0)  # Remove microseconds for comparison
    amount = 50.0
    notes = "Annual federation fee"
    
    command = AddFederationPaymentCommand(
        player_name=test_player.name,
        payment_date=payment_date,
        amount=amount,
        notes=notes,
        db_uri=temp_db_uri
    )
    
    result = add_federation_payment(command)
    
    # Verify the result
    assert result.id is not None
    assert result.player_name == test_player.name
    assert result.payment_date == payment_date
    assert result.amount == amount
    assert result.notes == notes
    assert result.created_at is not None
    
    # Verify database state
    db_path = temp_db_uri.replace('file://', '')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, player_name, payment_date, amount, notes
        FROM federation_payments
        WHERE id = ?
    """, (result.id,))
    row = cursor.fetchone()
    conn.close()
    
    assert row is not None
    assert row[0] == result.id
    assert row[1] == test_player.name
    assert datetime.fromisoformat(row[2]) == payment_date
    assert row[3] == amount
    assert row[4] == notes


def test_remove_last_federation_payment(temp_db_uri, test_player):
    """Test removing the most recent federation payment for a player."""
    # Add two payments with different dates
    payment1_date = datetime(2025, 1, 1, 12, 0, 0)
    payment2_date = datetime(2025, 2, 1, 12, 0, 0)  # More recent
    
    command1 = AddFederationPaymentCommand(
        player_name=test_player.name,
        payment_date=payment1_date,
        amount=50.0,
        notes="First payment",
        db_uri=temp_db_uri
    )
    
    command2 = AddFederationPaymentCommand(
        player_name=test_player.name,
        payment_date=payment2_date,
        amount=75.0,
        notes="Second payment",
        db_uri=temp_db_uri
    )
    
    payment1 = add_federation_payment(command1)
    payment2 = add_federation_payment(command2)
    
    # Verify both payments were added
    list_command = ListFederationPaymentsCommand(
        player_name=test_player.name,
        db_uri=temp_db_uri
    )
    _, payments_before = list_federation_payments(list_command)
    assert len(payments_before) == 2
    
    # Remove the latest payment
    remove_command = RemoveLastFederationPaymentCommand(
        player_name=test_player.name,
        db_uri=temp_db_uri
    )
    
    removed_payment = remove_last_federation_payment(remove_command)
    
    # Verify the correct payment was removed (the most recent one)
    assert removed_payment.id == payment2.id
    assert removed_payment.payment_date == payment2.payment_date
    assert removed_payment.amount == payment2.amount
    assert removed_payment.notes == payment2.notes
    
    # Verify only one payment remains
    _, payments_after = list_federation_payments(list_command)
    assert len(payments_after) == 1
    assert payments_after[0].id == payment1.id


def test_remove_last_federation_payment_none_exists(temp_db_uri, test_player):
    """Test removing a payment when none exists."""
    remove_command = RemoveLastFederationPaymentCommand(
        player_name=test_player.name,
        db_uri=temp_db_uri
    )
    
    result = remove_last_federation_payment(remove_command)
    
    # Should return None when no payments exist
    assert result is None


def test_list_federation_payments(temp_db_uri, test_player):
    """Test listing all federation payments for a player."""
    # Add multiple payments with different dates
    payments_to_add = [
        (datetime(2025, 1, 1, 12, 0, 0), 50.0, "First payment"),
        (datetime(2025, 2, 1, 12, 0, 0), 75.0, "Second payment"),
        (datetime(2025, 3, 1, 12, 0, 0), 100.0, "Third payment"),
    ]
    
    added_payments = []
    for payment_date, amount, notes in payments_to_add:
        command = AddFederationPaymentCommand(
            player_name=test_player.name,
            payment_date=payment_date,
            amount=amount,
            notes=notes,
            db_uri=temp_db_uri
        )
        added_payments.append(add_federation_payment(command))
    
    # List payments
    list_command = ListFederationPaymentsCommand(
        player_name=test_player.name,
        db_uri=temp_db_uri
    )
    
    player, payments = list_federation_payments(list_command)
    
    # Verify player details
    assert player.name == test_player.name
    assert player.phone == test_player.phone
    assert player.email == test_player.email
    
    # Verify all payments are listed, in correct order (most recent first)
    assert len(payments) == len(payments_to_add)
    
    # Check sort order - should be in reverse chronological order
    for i in range(len(payments) - 1):
        assert payments[i].payment_date > payments[i+1].payment_date
    
    # Check total amount calculation works in CLI
    total = sum(payment.amount for payment in payments)
    assert total == sum(amount for _, amount, _ in payments_to_add)


def test_player_not_found(temp_db_uri):
    """Test error when player not found."""
    # Try to add payment for non-existent player
    add_command = AddFederationPaymentCommand(
        player_name="NonExistentPlayer",
        payment_date=datetime.now(),
        amount=50.0,
        db_uri=temp_db_uri
    )
    
    with pytest.raises(ValueError) as excinfo:
        add_federation_payment(add_command)
    
    assert "not found" in str(excinfo.value)
    
    # Try to remove payment for non-existent player
    remove_command = RemoveLastFederationPaymentCommand(
        player_name="NonExistentPlayer",
        db_uri=temp_db_uri
    )
    
    with pytest.raises(ValueError) as excinfo:
        remove_last_federation_payment(remove_command)
    
    assert "not found" in str(excinfo.value)
    
    # Try to list payments for non-existent player
    list_command = ListFederationPaymentsCommand(
        player_name="NonExistentPlayer",
        db_uri=temp_db_uri
    )
    
    with pytest.raises(ValueError) as excinfo:
        list_federation_payments(list_command)
    
    assert "not found" in str(excinfo.value)