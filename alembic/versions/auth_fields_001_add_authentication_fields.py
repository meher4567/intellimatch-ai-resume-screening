"""Add authentication fields to User model

Revision ID: auth_fields_001
Revises: 
Create Date: 2024-11-24

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'auth_fields_001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add new columns to users table
    op.add_column('users', sa.Column('username', sa.String(), nullable=True))
    op.add_column('users', sa.Column('full_name', sa.String(), nullable=True))
    op.add_column('users', sa.Column('is_active', sa.Boolean(), nullable=True, server_default='true'))
    op.add_column('users', sa.Column('is_verified', sa.Boolean(), nullable=True, server_default='false'))
    op.add_column('users', sa.Column('updated_at', sa.DateTime(), nullable=True))
    op.add_column('users', sa.Column('last_login', sa.DateTime(), nullable=True))
    op.add_column('users', sa.Column('deleted_at', sa.DateTime(), nullable=True))
    
    # Rename password_hash to hashed_password if it exists
    try:
        op.alter_column('users', 'password_hash', new_column_name='hashed_password')
    except:
        pass  # Column might not exist or already renamed
    
    # Create unique index on username
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)
    
    # Update existing records to have username (use email as initial username)
    op.execute("UPDATE users SET username = email WHERE username IS NULL")
    
    # Make username NOT NULL after setting default values
    op.alter_column('users', 'username', nullable=False)


def downgrade() -> None:
    # Drop added columns
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_column('users', 'deleted_at')
    op.drop_column('users', 'last_login')
    op.drop_column('users', 'updated_at')
    op.drop_column('users', 'is_verified')
    op.drop_column('users', 'is_active')
    op.drop_column('users', 'full_name')
    op.drop_column('users', 'username')
    
    # Rename back
    try:
        op.alter_column('users', 'hashed_password', new_column_name='password_hash')
    except:
        pass
