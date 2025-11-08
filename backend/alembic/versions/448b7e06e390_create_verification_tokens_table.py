"""create_verification_tokens_table

Revision ID: 448b7e06e390
Revises: 0cdade979fc9
Create Date: 2025-11-08 02:16:35.545602

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '448b7e06e390'
down_revision: Union[str, Sequence[str], None] = '0cdade979fc9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'verification_tokens',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id'), nullable=False, index=True),
        sa.Column('token', sa.String(255), nullable=False, unique=True, index=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('is_used', sa.Boolean(), nullable=False, default=False),
        sa.Column('used_at', sa.DateTime(), nullable=True),
    )
    # Create compound index for expiration/usage queries
    op.create_index('idx_verification_expires', 'verification_tokens', ['expires_at', 'is_used'])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('idx_verification_expires', table_name='verification_tokens')
    op.drop_table('verification_tokens')
