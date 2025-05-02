from fastapi import APIRouter, Depends, status
import sqlalchemy
from src.api import auth
from src import database as db

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(auth.get_api_key)],
)


@router.post("/reset", status_code=status.HTTP_204_NO_CONTENT)
def reset():
    """
    Reset the game state. Gold goes to 100, all potions are removed from
    inventory, and all barrels are removed from inventory. Carts are all reset.
    """

    # clear all data in the database
    print("Resetting state...")
    with db.engine.begin() as connection:
        connection.execute(
            sqlalchemy.text(
                """
                DELETE FROM ledger_entries
                """
            )
        )
        connection.execute(
            sqlalchemy.text(
                """
                DELETE FROM cart_items
                """
            )
        )
        connection.execute(
            sqlalchemy.text(
                """
                DELETE FROM carts
                """
            )
        )
        connection.execute(
            sqlalchemy.text(
                """
                DELETE FROM account_transactions
                """
            )
        )
        connection.execute(
            sqlalchemy.text(
                """
                DELETE FROM processed_requests
                """
            )
        )
        # Reset gold to 100
        transaction_id = connection.execute(
            sqlalchemy.text(
                """
                INSERT INTO account_transactions (transaction_type)
                VALUES ('customer_purchase')
                RETURNING transaction_id
                """
            )
        ).scalar_one()
        connection.execute(
            sqlalchemy.text(
                """
                INSERT INTO ledger_entries (transaction_id, change_red_ml, change_green_ml, change_blue_ml, change_gold, change_potions)
                VALUES (:transaction_id, 0, 0, 0, 100, 0)
                """
            ),
            {"transaction_id": transaction_id},
        )

        # # reset business logic table
        # connection.execute(
        #     sqlalchemy.text(
        #         """
        #         UPDATE business_logic
        #         SET ml_capacity = 1, potions_capacity = 1
        #         """
        #     )
        # )
