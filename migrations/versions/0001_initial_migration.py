"""Initial migration

Revision ID: 0001
Revises: 
Create Date: 2025-01-24 12:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create weather_records table
    op.create_table('weather_records',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('city', sa.String(length=100), nullable=False),
        sa.Column('temperature', sa.Float(), nullable=False),
        sa.Column('humidity', sa.Integer(), nullable=False),
        sa.Column('wind_speed', sa.Float(), nullable=False),
        sa.Column('description', sa.String(length=200), nullable=False),
        sa.Column('recorded_at', sa.DateTime(), nullable=False),
        sa.Column('timezone', sa.String(length=50), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create index on city and recorded_at for better query performance
    op.create_index('ix_weather_records_city', 'weather_records', ['city'])
    op.create_index('ix_weather_records_recorded_at', 'weather_records', ['recorded_at'])


def downgrade() -> None:
    # Drop indexes first
    op.drop_index('ix_weather_records_recorded_at', table_name='weather_records')
    op.drop_index('ix_weather_records_city', table_name='weather_records')
    
    # Drop table
    op.drop_table('weather_records')
