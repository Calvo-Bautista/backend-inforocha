"""refactor client fields and add printers table

Revision ID: c7de11a5dcde
Revises: 55b90ee20d53
Create Date: 2026-02-10 19:19:30.844469

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text


# revision identifiers, used by Alembic.
revision: str = 'c7de11a5dcde'
down_revision: Union[str, None] = '55b90ee20d53'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Rename tipo_cliente to priority and make it nullable in one step (MySQL CHANGE COLUMN)
    op.execute("""
        ALTER TABLE clients 
        CHANGE COLUMN tipo_cliente priority ENUM('alta', 'media', 'baja') NULL
    """)
    
    # 2. Create client_printers table
    op.create_table(
        'client_printers',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('client_id', sa.Integer(), sa.ForeignKey('clients.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('printer_model', sa.String(255), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    
    # 3. Migrate data from maquinas to client_printers
    # Get all clients with maquinas data
    connection = op.get_bind()
    clients = connection.execute(text("SELECT id, maquinas FROM clients WHERE maquinas IS NOT NULL AND maquinas != ''"))
    
    for client_id, maquinas in clients:
        if maquinas:
            # Split by common delimiters (comma, semicolon, newline)
            printers = [p.strip() for p in maquinas.replace(';', ',').replace('\n', ',').split(',') if p.strip()]
            
            # Insert each printer
            for printer in printers:
                connection.execute(
                    text("INSERT INTO client_printers (client_id, printer_model) VALUES (:client_id, :printer_model)"),
                    {"client_id": client_id, "printer_model": printer}
                )
    
    # Note: Keeping maquinas column for backward compatibility
    # Can be dropped later: op.drop_column('clients', 'maquinas')


def downgrade() -> None:
    # 1. Migrate data back from client_printers to maquinas (if needed)
    connection = op.get_bind()
    clients_with_printers = connection.execute(
        text("""
            SELECT client_id, GROUP_CONCAT(printer_model SEPARATOR ', ') as printers
            FROM client_printers
            GROUP BY client_id
        """)
    )
    
    for client_id, printers in clients_with_printers:
        connection.execute(
            text("UPDATE clients SET maquinas = :printers WHERE id = :client_id"),
            {"printers": printers, "client_id": client_id}
        )
    
    # 2. Drop client_printers table
    op.drop_table('client_printers')
    
    # 3. Rename priority back to tipo_cliente and make it NOT NULL (MySQL CHANGE COLUMN)
    op.execute("""
        ALTER TABLE clients 
        CHANGE COLUMN priority tipo_cliente ENUM('alta', 'media', 'baja') NOT NULL
    """)
