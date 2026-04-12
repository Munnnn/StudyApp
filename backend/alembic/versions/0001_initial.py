"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-04-11
"""
from typing import Sequence, Union
import uuid

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# These references are only used as column types — create_type=False means
# "the type already exists in the DB; don't try to CREATE TYPE again".
source_type_col = postgresql.ENUM(
    "manual", "csv", "anki_import",
    name="source_type_enum",
    create_type=False,
)
mastery_level_col = postgresql.ENUM(
    "weak", "fragile", "developing", "strong",
    name="mastery_level_enum",
    create_type=False,
)


def upgrade() -> None:
    # --- 1. Create enum types via PL/pgSQL so this is idempotent -----------
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE source_type_enum AS ENUM ('manual', 'csv', 'anki_import');
        EXCEPTION WHEN duplicate_object THEN NULL;
        END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE mastery_level_enum AS ENUM ('weak', 'fragile', 'developing', 'strong');
        EXCEPTION WHEN duplicate_object THEN NULL;
        END $$;
    """)

    # --- 2. Create tables (using create_type=False refs above) --------------
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column("device_id", sa.String, nullable=False, unique=True),
        sa.Column("display_name", sa.String, nullable=True),
        sa.Column("notification_interval_min", sa.Integer, nullable=False, server_default="30"),
        sa.Column("quiet_hours_start", sa.String, nullable=True),
        sa.Column("quiet_hours_end", sa.String, nullable=True),
        sa.Column("paused", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("ix_users_device_id", "users", ["device_id"])

    op.create_table(
        "decks",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column("owner_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("source_type", source_type_col, nullable=False, server_default="manual"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("ix_decks_owner_id", "decks", ["owner_id"])

    op.create_table(
        "cards",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column("deck_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("decks.id", ondelete="CASCADE"), nullable=False),
        sa.Column("front", sa.Text, nullable=False),
        sa.Column("back", sa.Text, nullable=False),
        sa.Column("system_tag", sa.String(100), nullable=True),
        sa.Column("topic_tag", sa.String(100), nullable=True),
        sa.Column("difficulty", sa.SmallInteger, nullable=False, server_default="2"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("ix_cards_deck_id", "cards", ["deck_id"])

    op.create_table(
        "generated_questions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column("card_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("cards.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("attending_question", sa.Text, nullable=False),
        sa.Column("correct_answer", sa.Text, nullable=False),
        sa.Column("step_by_step_explanation", sa.Text, nullable=False),
        sa.Column("wrong_answer_analysis", postgresql.JSONB, nullable=False, server_default="[]"),
        sa.Column("high_yield_takeaway", sa.Text, nullable=False),
        sa.Column("follow_up_questions", postgresql.JSONB, nullable=False, server_default="[]"),
        sa.Column("mcq_options", postgresql.JSONB, nullable=False, server_default="[]"),
        sa.Column("ai_provider", sa.String(50), nullable=True),
        sa.Column("ai_model", sa.String(100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    op.create_table(
        "question_attempts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("generated_question_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("generated_questions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("typed_answer_raw", sa.Text, nullable=True),
        sa.Column("typed_answer_score", sa.SmallInteger, nullable=True),
        sa.Column("mcq_selected_index", sa.SmallInteger, nullable=True),
        sa.Column("mcq_correct", sa.Boolean, nullable=True),
        sa.Column("response_time_text_ms", sa.Integer, nullable=True),
        sa.Column("response_time_mcq_ms", sa.Integer, nullable=True),
        sa.Column("mastery_level", mastery_level_col, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("ix_attempts_user_id", "question_attempts", ["user_id"])
    op.create_index("ix_attempts_gq_id", "question_attempts", ["generated_question_id"])

    op.create_table(
        "schedule_state",
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("card_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("cards.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("next_due_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("interval_min", sa.Integer, nullable=False, server_default="10"),
        sa.Column("last_mastery", mastery_level_col, nullable=False, server_default="weak"),
        sa.Column("consecutive_strong", sa.Integer, nullable=False, server_default="0"),
        sa.Column("total_attempts", sa.Integer, nullable=False, server_default="0"),
    )
    op.create_index("ix_schedule_user_due", "schedule_state", ["user_id", "next_due_at"])


def downgrade() -> None:
    op.drop_table("schedule_state")
    op.drop_table("question_attempts")
    op.drop_table("generated_questions")
    op.drop_table("cards")
    op.drop_table("decks")
    op.drop_table("users")
    op.execute("DROP TYPE IF EXISTS source_type_enum")
    op.execute("DROP TYPE IF EXISTS mastery_level_enum")
