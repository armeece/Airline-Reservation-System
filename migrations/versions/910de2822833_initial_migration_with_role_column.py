"""Initial migration with role column

Revision ID: 910de2822833
Revises: 
Create Date: 2024-11-30 16:00:05.978563

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '910de2822833'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands adjusted for SQLite compatibility ###

    # Add the 'role' column with a default value
    with op.batch_alter_table('users') as batch_op:
        batch_op.add_column(sa.Column('role', sa.String(length=50), nullable=False, server_default='customer'))

    # Remove unnecessary columns in 'bookings'
    with op.batch_alter_table('bookings') as batch_op:
        if 'seat_class' in batch_op.get_table_comment():
            batch_op.drop_column('seat_class')

    # Adjustments for altering column types in SQLite are omitted
    # If changes are critical, consider recreating the table with the desired schema.

    # ### end Alembic commands ###


def downgrade():
    # ### commands for downgrading ###

    # Remove the 'role' column
    with op.batch_alter_table('users') as batch_op:
        batch_op.drop_column('role')

    # Restore the 'seat_class' column in 'bookings'
    with op.batch_alter_table('bookings') as batch_op:
        batch_op.add_column(sa.Column('seat_class', sa.String(length=50), nullable=False))

    # Note: Recreate indices or handle column type changes manually if necessary.

    # ### end Alembic commands ###
