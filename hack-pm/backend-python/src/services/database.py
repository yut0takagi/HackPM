"""
Database configuration and models for hack-pm
"""
import os
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Boolean, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.sql import func
from datetime import datetime

# Database URL
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./hack_pm.db")

# Create engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

# Create session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class
Base = declarative_base()

class Repository(Base):
    __tablename__ = "repos"
    
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    owner = Column(String, nullable=False)
    default_branch = Column(String, default="main")
    visibility = Column(String, default="private")
    description = Column(Text)
    html_url = Column(String)
    clone_url = Column(String)
    ssh_url = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    branches = relationship("Branch", back_populates="repository", cascade="all, delete-orphan")
    pull_requests = relationship("PullRequest", back_populates="repository", cascade="all, delete-orphan")
    issues = relationship("Issue", back_populates="repository", cascade="all, delete-orphan")
    ci_runs = relationship("CIRun", back_populates="repository", cascade="all, delete-orphan")
    events = relationship("Event", back_populates="repository", cascade="all, delete-orphan")

class Branch(Base):
    __tablename__ = "branches"
    
    id = Column(Integer, primary_key=True, index=True)
    repo_id = Column(Integer, ForeignKey("repos.id"), nullable=False)
    name = Column(String, nullable=False)
    head_sha = Column(String, nullable=False)
    is_default = Column(Boolean, default=False)
    is_protected = Column(Boolean, default=False)
    last_commit_message = Column(Text)
    last_commit_author = Column(String)
    last_commit_date = Column(DateTime)
    pushed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    repository = relationship("Repository", back_populates="branches")
    
    # Indexes
    __table_args__ = (
        Index('idx_branch_repo_name', 'repo_id', 'name'),
        Index('idx_branch_updated', 'repo_id', 'updated_at'),
    )

class PullRequest(Base):
    __tablename__ = "pull_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    repo_id = Column(Integer, ForeignKey("repos.id"), nullable=False)
    number = Column(Integer, nullable=False)
    title = Column(String, nullable=False)
    body = Column(Text)
    author = Column(String, nullable=False)
    author_avatar = Column(String)
    state = Column(String, nullable=False)  # open, closed, merged
    draft = Column(Boolean, default=False)
    head_ref = Column(String, nullable=False)
    base_ref = Column(String, nullable=False)
    head_sha = Column(String)
    merge_commit_sha = Column(String)
    html_url = Column(String)
    mergeable = Column(Boolean)
    merged_at = Column(DateTime)
    closed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    repository = relationship("Repository", back_populates="pull_requests")
    
    # Indexes
    __table_args__ = (
        Index('idx_pr_repo_number', 'repo_id', 'number'),
        Index('idx_pr_state', 'repo_id', 'state'),
        Index('idx_pr_updated', 'repo_id', 'updated_at'),
    )

class Issue(Base):
    __tablename__ = "issues"
    
    id = Column(Integer, primary_key=True, index=True)
    repo_id = Column(Integer, ForeignKey("repos.id"), nullable=False)
    number = Column(Integer, nullable=False)
    title = Column(String, nullable=False)
    body = Column(Text)
    author = Column(String, nullable=False)
    author_avatar = Column(String)
    state = Column(String, nullable=False)  # open, closed
    labels_json = Column(Text)  # JSON string of labels
    assignees_json = Column(Text)  # JSON string of assignees
    milestone = Column(String)
    html_url = Column(String)
    closed_at = Column(DateTime)
    # Time-boxed development fields
    estimated_hours = Column(Integer)  # Estimated completion time in hours
    deadline = Column(DateTime)  # Hard deadline for completion
    time_box_start = Column(DateTime)  # When work started on this issue
    time_box_end = Column(DateTime)  # When time box expires
    priority_escalated = Column(Boolean, default=False)  # Auto-escalated due to deadline
    hackathon_phase = Column(String)  # planning, development, testing, presentation
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    repository = relationship("Repository", back_populates="issues")
    
    # Indexes
    __table_args__ = (
        Index('idx_issue_repo_number', 'repo_id', 'number'),
        Index('idx_issue_state', 'repo_id', 'state'),
        Index('idx_issue_updated', 'repo_id', 'updated_at'),
    )

class CIRun(Base):
    __tablename__ = "ci_runs"
    
    id = Column(Integer, primary_key=True, index=True)
    repo_id = Column(Integer, ForeignKey("repos.id"), nullable=False)
    run_id = Column(String, nullable=False)  # GitHub run ID
    workflow_name = Column(String, nullable=False)
    workflow_id = Column(String)
    status = Column(String, nullable=False)  # queued, in_progress, completed
    conclusion = Column(String)  # success, failure, neutral, cancelled, skipped, timed_out, action_required
    head_branch = Column(String, nullable=False)
    head_sha = Column(String, nullable=False)
    event = Column(String)  # push, pull_request, etc.
    actor = Column(String)
    html_url = Column(String)
    jobs_url = Column(String)
    logs_url = Column(String)
    run_started_at = Column(DateTime)
    run_updated_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    repository = relationship("Repository", back_populates="ci_runs")
    
    # Indexes
    __table_args__ = (
        Index('idx_ci_repo_run', 'repo_id', 'run_id'),
        Index('idx_ci_status', 'repo_id', 'status'),
        Index('idx_ci_updated', 'repo_id', 'updated_at'),
    )

class Event(Base):
    __tablename__ = "events"
    
    id = Column(Integer, primary_key=True, index=True)
    repo_id = Column(Integer, ForeignKey("repos.id"), nullable=False)
    event_type = Column(String, nullable=False)  # push, pull_request, issues, etc.
    action = Column(String)  # opened, closed, synchronize, etc.
    payload_json = Column(Text, nullable=False)  # Full GitHub payload
    delivery_id = Column(String, unique=True)  # GitHub delivery ID
    actor = Column(String)
    ref = Column(String)  # branch/tag reference
    before_sha = Column(String)
    after_sha = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    repository = relationship("Repository", back_populates="events")
    
    # Indexes
    __table_args__ = (
        Index('idx_event_repo_type', 'repo_id', 'event_type'),
        Index('idx_event_created', 'repo_id', 'created_at'),
        Index('idx_event_delivery', 'delivery_id'),
    )

class HackathonTimeBox(Base):
    __tablename__ = "hackathon_timeboxes"
    
    id = Column(Integer, primary_key=True, index=True)
    repo_id = Column(Integer, ForeignKey("repos.id"), nullable=False)
    name = Column(String, nullable=False)  # e.g., "Sprint 1", "Feature Development Phase"
    phase = Column(String, nullable=False)  # planning, development, testing, presentation
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    repository = relationship("Repository")
    
    # Indexes
    __table_args__ = (
        Index('idx_timebox_repo_active', 'repo_id', 'is_active'),
        Index('idx_timebox_phase', 'repo_id', 'phase'),
    )

# Create all tables
def create_tables():
    """Create all tables and run migrations"""
    Base.metadata.create_all(bind=engine)
    
    # Run migrations after creating tables
    try:
        from .migrations import run_migrations
        run_migrations()
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error running migrations: {e}")

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()