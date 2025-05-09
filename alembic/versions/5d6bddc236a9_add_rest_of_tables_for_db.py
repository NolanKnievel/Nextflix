"""add rest of tables for db

Revision ID: 5d6bddc236a9
Revises: e26499287814
Create Date: 2025-05-09 12:13:38.992711

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5d6bddc236a9'
down_revision: Union[str, None] = 'e26499287814'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ---------------- media - media_id, media_type ----------------
    op.create_table(
        'media',
        sa.Column('media_id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('media_type', sa.String(10), nullable=False)
    )

    # media_type - must be either movie or show
    op.create_check_constraint(
        'ck_media_type',
        'media',
        sa.text("media_type IN ('movie', 'show')")
    )





    # ---------------- tv_shows - media_id, title, total_episodes, total_seasons, director ----------------
    op.create_table(
        'tv_shows',
        sa.Column('media_id', sa.Integer, sa.ForeignKey('media.media_id'), primary_key=True),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('total_episodes', sa.Integer, nullable=False),
        sa.Column('total_seasons', sa.Integer, nullable=False),
        sa.Column('director', sa.String(255), nullable=False)
    )

    # total_episodes - must be greater than 0
    op.create_check_constraint(
        'ck_total_episodes',
        'tv_shows',
        sa.text("total_episodes > 0")
    )
    # total_seasons - must be greater than 0
    op.create_check_constraint(
        'ck_total_seasons',
        'tv_shows',
        sa.text("total_seasons > 0")
    )

    # title - must be unique
    op.create_unique_constraint(
        'uq_tv_shows_title',
        'tv_shows',
        ['title']
    )





    # ---------------- movies - media_id, title, length, director ----------------
    op.create_table(
        'movies',
        sa.Column('media_id', sa.Integer, sa.ForeignKey('media.media_id'), primary_key=True),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('length', sa.Integer, nullable=False),
        sa.Column('director', sa.String(255), nullable=False)
    )
    # length - must be greater than 0
    op.create_check_constraint(
        'ck_length',
        'movies',
        sa.text("length > 0")
    )

    # title - must be unique
    op.create_unique_constraint(
        'uq_movies_title',
        'movies',
        ['title']
    )


    # ---------------- watchlists - user_id, media_id, have_watched ----------------

    op.create_table(
        'watchlists',
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id'), primary_key=True),
        sa.Column('media_id', sa.Integer, sa.ForeignKey('media.media_id'), primary_key=True),
        sa.Column('have_watched', sa.Boolean, nullable=False)
    )

    # user_id and media_id - must be unique together - users only have one watchlist entry per media
    op.create_unique_constraint(
        'uq_watchlists_user_id_media_id',
        'watchlists',
        ['user_id', 'media_id']
    )


    # ---------------- reviews - user_id, media_id, rating, review ----------------
    op.create_table(
        'reviews',
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id'), primary_key=True),
        sa.Column('media_id', sa.Integer, sa.ForeignKey('media.media_id'), primary_key=True),
        sa.Column('rating', sa.Float, nullable=False),
        sa.Column('review', sa.String(255), nullable=False)
    )

    # user_id and media_id - must be unique together - users only have one review per media
    op.create_unique_constraint(
        'uq_reviews_user_id_media_id',
        'reviews',
        ['user_id', 'media_id']
    )




def downgrade() -> None:
    op.drop_table('reviews')
    op.drop_table('watchlists')
    op.drop_table('movies')
    op.drop_table('tv_shows')
    op.drop_table('media')
    
    
