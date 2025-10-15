"""add_document_upload_id_to_processing_tasks

Revision ID: 5be054bd6587
Revises: fd73eebc87c1
Create Date: 2025-01-14 01:17:24.164593

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5be054bd6587'
down_revision: Union[str, None] = 'fd73eebc87c1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add document_upload_id field
    bind = op.get_bind()
    is_sqlite = bind.dialect.name == 'sqlite'
    
    # Add column
    op.add_column('processing_tasks', sa.Column('document_upload_id', sa.Integer(), nullable=True))
    
    # SQLite doesn't support adding foreign keys after table creation
    if not is_sqlite:
        op.create_foreign_key(
            'processing_tasks_document_upload_id_fkey',
            'processing_tasks',
            'document_uploads',
            ['document_upload_id'],
            ['id']
        )


def downgrade() -> None:
    # Remove foreign key and column
    bind = op.get_bind()
    is_sqlite = bind.dialect.name == 'sqlite'
    
    if not is_sqlite:
        op.drop_constraint('processing_tasks_document_upload_id_fkey', 'processing_tasks', type_='foreignkey')
    
    op.drop_column('processing_tasks', 'document_upload_id')
