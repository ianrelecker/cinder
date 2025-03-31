"""
Database models for Caldera.

This module defines the SQLAlchemy models for Caldera's core entities.
"""

import datetime
import uuid
from typing import List, Dict, Any, Optional, Set, Union

from sqlalchemy import Column, Integer, String, ForeignKey, Table, DateTime, Boolean, Text, JSON, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref

Base = declarative_base()

# Association tables for many-to-many relationships
ability_adversary = Table(
    'ability_adversary', Base.metadata,
    Column('ability_id', String(36), ForeignKey('abilities.id')),
    Column('adversary_id', String(36), ForeignKey('adversaries.id'))
)

ability_operation = Table(
    'ability_operation', Base.metadata,
    Column('ability_id', String(36), ForeignKey('abilities.id')),
    Column('operation_id', String(36), ForeignKey('operations.id'))
)

agent_operation = Table(
    'agent_operation', Base.metadata,
    Column('agent_id', String(36), ForeignKey('agents.id')),
    Column('operation_id', String(36), ForeignKey('operations.id'))
)

class Ability(Base):
    """
    An ability represents a specific ATT&CK technique implementation.
    """
    __tablename__ = 'abilities'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    ability_id = Column(String(36), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    tactic = Column(String(255))
    technique_id = Column(String(50))
    technique_name = Column(String(255))
    privilege = Column(String(50))
    repeatable = Column(Boolean, default=False)
    singleton = Column(Boolean, default=False)
    plugin = Column(String(50))
    access = Column(String(10))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.datetime.utcnow)
    
    # Relationships
    executors = relationship("Executor", back_populates="ability", cascade="all, delete-orphan")
    requirements = relationship("Requirement", back_populates="ability", cascade="all, delete-orphan")
    adversaries = relationship("Adversary", secondary=ability_adversary, back_populates="abilities")
    operations = relationship("Operation", secondary=ability_operation, back_populates="abilities")
    
    def __repr__(self):
        return f"<Ability(ability_id='{self.ability_id}', name='{self.name}')>"


class Executor(Base):
    """
    An executor represents a specific implementation of an ability for a platform.
    """
    __tablename__ = 'executors'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    ability_id = Column(String(36), ForeignKey('abilities.id'), nullable=False)
    name = Column(String(255), nullable=False)
    platform = Column(String(50), nullable=False)
    command = Column(Text)
    code = Column(Text)
    language = Column(String(50))
    build_target = Column(String(255))
    timeout = Column(Integer, default=60)
    cleanup = Column(Text)
    
    # Relationships
    ability = relationship("Ability", back_populates="executors")
    parsers = relationship("Parser", back_populates="executor", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Executor(name='{self.name}', platform='{self.platform}')>"


class Parser(Base):
    """
    A parser processes the output of an executor.
    """
    __tablename__ = 'parsers'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    executor_id = Column(String(36), ForeignKey('executors.id'), nullable=False)
    module = Column(String(255), nullable=False)
    config = Column(JSON)
    
    # Relationships
    executor = relationship("Executor", back_populates="parsers")
    
    def __repr__(self):
        return f"<Parser(module='{self.module}')>"


class Requirement(Base):
    """
    A requirement is a condition that must be met for an ability to be used.
    """
    __tablename__ = 'requirements'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    ability_id = Column(String(36), ForeignKey('abilities.id'), nullable=False)
    module = Column(String(255), nullable=False)
    relationship_match = Column(JSON)
    
    # Relationships
    ability = relationship("Ability", back_populates="requirements")
    
    def __repr__(self):
        return f"<Requirement(module='{self.module}')>"


class Adversary(Base):
    """
    An adversary is a collection of abilities that represent a threat actor.
    """
    __tablename__ = 'adversaries'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    adversary_id = Column(String(36), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    plugin = Column(String(50))
    access = Column(String(10))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.datetime.utcnow)
    
    # Relationships
    abilities = relationship("Ability", secondary=ability_adversary, back_populates="adversaries")
    operations = relationship("Operation", back_populates="adversary")
    
    def __repr__(self):
        return f"<Adversary(adversary_id='{self.adversary_id}', name='{self.name}')>"


class Agent(Base):
    """
    An agent is a deployed instance of Caldera on a target system.
    """
    __tablename__ = 'agents'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    paw = Column(String(36), unique=True, nullable=False)
    host = Column(String(255))
    username = Column(String(255))
    group = Column(String(255))
    architecture = Column(String(50))
    platform = Column(String(50))
    location = Column(String(255))
    pid = Column(Integer)
    ppid = Column(Integer)
    trusted = Column(Boolean, default=True)
    sleep_min = Column(Integer, default=30)
    sleep_max = Column(Integer, default=60)
    watchdog = Column(Integer)
    contact = Column(String(50))
    pending_contact = Column(String(50))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    last_seen = Column(DateTime)
    last_trusted_seen = Column(DateTime)
    
    # Relationships
    operations = relationship("Operation", secondary=agent_operation, back_populates="agents")
    links = relationship("Link", back_populates="agent", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Agent(paw='{self.paw}', platform='{self.platform}')>"


class Operation(Base):
    """
    An operation is a collection of abilities executed against a set of agents.
    """
    __tablename__ = 'operations'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    adversary_id = Column(String(36), ForeignKey('adversaries.id'))
    state = Column(String(20), default='created')
    planner = Column(String(50))
    jitter = Column(Float, default=0.0)
    start = Column(DateTime)
    finish = Column(DateTime)
    phase = Column(String(50))
    obfuscator = Column(String(50))
    autonomous = Column(Integer, default=1)
    chain_mode = Column(String(50), default='batch')
    auto_close = Column(Boolean, default=False)
    visibility = Column(Integer, default=50)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relationships
    adversary = relationship("Adversary", back_populates="operations")
    agents = relationship("Agent", secondary=agent_operation, back_populates="operations")
    abilities = relationship("Ability", secondary=ability_operation, back_populates="operations")
    links = relationship("Link", back_populates="operation", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Operation(id='{self.id}', name='{self.name}', state='{self.state}')>"


class Link(Base):
    """
    A link is a specific execution of an ability on an agent.
    """
    __tablename__ = 'links'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    operation_id = Column(String(36), ForeignKey('operations.id'), nullable=False)
    agent_id = Column(String(36), ForeignKey('agents.id'), nullable=False)
    ability_id = Column(String(36), ForeignKey('abilities.id'), nullable=False)
    command = Column(Text)
    status = Column(Integer, default=0)
    score = Column(Integer, default=0)
    jitter = Column(Integer, default=0)
    cleanup = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    decide = Column(DateTime)
    collect = Column(DateTime)
    finish = Column(DateTime)
    
    # Relationships
    operation = relationship("Operation", back_populates="links")
    agent = relationship("Agent", back_populates="links")
    ability = relationship("Ability")
    
    def __repr__(self):
        return f"<Link(id='{self.id}', status={self.status})>"


class Objective(Base):
    """
    An objective is a goal for an operation.
    """
    __tablename__ = 'objectives'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    description = Column(Text)
    plugin = Column(String(50))
    access = Column(String(10))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relationships
    goals = relationship("Goal", back_populates="objective", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Objective(id='{self.id}', name='{self.name}')>"


class Goal(Base):
    """
    A goal is a specific target within an objective.
    """
    __tablename__ = 'goals'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    objective_id = Column(String(36), ForeignKey('objectives.id'), nullable=False)
    target = Column(String(255))
    value = Column(String(255))
    count = Column(Integer, default=1)
    achieved = Column(Boolean, default=False)
    
    # Relationships
    objective = relationship("Objective", back_populates="goals")
    
    def __repr__(self):
        return f"<Goal(target='{self.target}', value='{self.value}')>"


class Plugin(Base):
    """
    A plugin extends Caldera's functionality.
    """
    __tablename__ = 'plugins'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False, unique=True)
    enabled = Column(Boolean, default=True)
    description = Column(Text)
    address = Column(String(255))
    data_dir = Column(String(255))
    access = Column(String(10))
    
    def __repr__(self):
        return f"<Plugin(name='{self.name}', enabled={self.enabled})>"


class Source(Base):
    """
    A source provides facts for operations.
    """
    __tablename__ = 'sources'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    plugin = Column(String(50))
    facts = Column(JSON)
    
    def __repr__(self):
        return f"<Source(id='{self.id}', name='{self.name}')>"


class Planner(Base):
    """
    A planner determines how abilities are executed in an operation.
    """
    __tablename__ = 'planners'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False, unique=True)
    module = Column(String(255), nullable=False)
    description = Column(Text)
    stopping_conditions = Column(JSON)
    params = Column(JSON)
    allow_repeats = Column(Boolean, default=False)
    
    def __repr__(self):
        return f"<Planner(name='{self.name}')>"


class Schedule(Base):
    """
    A schedule defines when operations should run.
    """
    __tablename__ = 'schedules'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    schedule = Column(String(255), nullable=False)
    task_id = Column(String(36))
    
    def __repr__(self):
        return f"<Schedule(name='{self.name}', schedule='{self.schedule}')>"


class DataEncoder(Base):
    """
    A data encoder transforms data for transmission.
    """
    __tablename__ = 'data_encoders'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False, unique=True)
    description = Column(Text)
    
    def __repr__(self):
        return f"<DataEncoder(name='{self.name}')>"


class Obfuscator(Base):
    """
    An obfuscator transforms commands to avoid detection.
    """
    __tablename__ = 'obfuscators'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False, unique=True)
    description = Column(Text)
    
    def __repr__(self):
        return f"<Obfuscator(name='{self.name}')>"
