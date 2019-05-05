"""empty message

Revision ID: 27e80a1b23b4
Revises: 
Create Date: 2019-04-02 19:56:55.068274

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '27e80a1b23b4'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('course',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('cid', sa.String(length=20), nullable=False),
    sa.Column('name', sa.String(length=80), nullable=False),
    sa.Column('school', sa.String(length=10), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('professor',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=80), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('prof_course',
    sa.Column('cname', sa.String(length=80), nullable=False),
    sa.Column('pname', sa.String(length=80), nullable=False),
    sa.ForeignKeyConstraint(['cname'], ['course.name'], ),
    sa.ForeignKeyConstraint(['pname'], ['professor.name'], ),
    sa.PrimaryKeyConstraint('cname', 'pname', name='prof_course_pk')
    )
    op.create_table('review',
    sa.Column('reviewer', sa.String(length=80), nullable=False),
    sa.Column('pname', sa.String(length=80), nullable=False),
    sa.Column('cname', sa.String(length=80), nullable=False),
    sa.Column('score1', sa.Float(), nullable=False),
    sa.Column('score2', sa.Float(), nullable=False),
    sa.Column('score3', sa.Float(), nullable=False),
    sa.Column('year', sa.Integer(), nullable=True),
    sa.Column('school', sa.String(length=10), nullable=True),
    sa.Column('comment', sa.String(length=300), nullable=True),
    sa.Column('advice', sa.String(length=300), nullable=True),
    sa.ForeignKeyConstraint(['pname', 'cname'], ['prof_course.pname', 'prof_course.cname'], ),
    sa.PrimaryKeyConstraint('reviewer', 'pname', 'cname')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('review')
    op.drop_table('prof_course')
    op.drop_table('professor')
    op.drop_table('course')
    # ### end Alembic commands ###
