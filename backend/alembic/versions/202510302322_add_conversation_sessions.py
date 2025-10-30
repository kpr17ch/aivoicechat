"""add conversation_sessions table"""

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision = "202510302322"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if "conversation_sessions" in inspector.get_table_names():
        existing_indexes = {
            index["name"] for index in inspector.get_indexes("conversation_sessions")
        }
        if "ix_conversation_sessions_stream_sid" not in existing_indexes:
            op.create_index(
                "ix_conversation_sessions_stream_sid",
                "conversation_sessions",
                ["stream_sid"],
                unique=True,
            )
        return

    op.create_table(
        "conversation_sessions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("stream_sid", sa.String(length=128), nullable=False),
        sa.Column("state", sa.String(length=50), nullable=False, server_default="initialized"),
        sa.Column("started_at", sa.DateTime(), nullable=True),
        sa.Column("ended_at", sa.DateTime(), nullable=True),
        sa.Column("duration_seconds", sa.Integer(), nullable=True),
        sa.Column("turn_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("user_phone", sa.String(length=50), nullable=True),
        sa.Column("latest_user_text", sa.Text(), nullable=True),
        sa.Column("latest_assistant_text", sa.Text(), nullable=True),
        sa.Column("data_version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("metadata_json", sa.JSON(), nullable=True),
        sa.Column("transcript_json", sa.JSON(), nullable=True),
        sa.Column("transcript_text", sa.Text(), nullable=True),
        sa.Column("transcript_json_path", sa.String(length=500), nullable=True),
        sa.Column("transcript_txt_path", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index(
        "ix_conversation_sessions_stream_sid",
        "conversation_sessions",
        ["stream_sid"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index("ix_conversation_sessions_stream_sid", table_name="conversation_sessions")
    op.drop_table("conversation_sessions")
