"""
Repository classes for database operations.

This module implements the repository pattern for database operations,
providing a clean interface for interacting with the database.
"""

from typing import List, Dict, Any, Optional, TypeVar, Generic, Type, Union
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import logging

from app.database.models import (
    Base, Ability, Executor, Parser, Requirement, Adversary, Agent,
    Operation, Link, Objective, Goal, Plugin, Source, Planner,
    Schedule, DataEncoder, Obfuscator
)

T = TypeVar('T', bound=Base)

class Repository(Generic[T]):
    """
    Base repository for database operations.
    
    This class provides generic CRUD operations for database entities.
    """
    
    def __init__(self, session: Session, model_class: Type[T]):
        """
        Initialize the repository.
        
        Args:
            session: SQLAlchemy session
            model_class: Model class for this repository
        """
        self.session = session
        self.model_class = model_class
        self.logger = logging.getLogger(f'repository.{model_class.__name__.lower()}')
    
    def get_by_id(self, entity_id: str) -> Optional[T]:
        """
        Get entity by ID.
        
        Args:
            entity_id: Entity ID
            
        Returns:
            Entity or None if not found
        """
        try:
            return self.session.query(self.model_class).filter_by(id=entity_id).first()
        except SQLAlchemyError as e:
            self.logger.error(f"Error getting {self.model_class.__name__} by ID: {e}")
            return None
    
    def get_all(self) -> List[T]:
        """
        Get all entities.
        
        Returns:
            List of entities
        """
        try:
            return self.session.query(self.model_class).all()
        except SQLAlchemyError as e:
            self.logger.error(f"Error getting all {self.model_class.__name__}s: {e}")
            return []
    
    def find(self, criteria: Dict[str, Any]) -> List[T]:
        """
        Find entities matching criteria.
        
        Args:
            criteria: Dictionary of field-value pairs to match
            
        Returns:
            List of matching entities
        """
        try:
            return self.session.query(self.model_class).filter_by(**criteria).all()
        except SQLAlchemyError as e:
            self.logger.error(f"Error finding {self.model_class.__name__}s: {e}")
            return []
    
    def add(self, entity: T) -> Optional[T]:
        """
        Add a new entity.
        
        Args:
            entity: Entity to add
            
        Returns:
            Added entity or None if error
        """
        try:
            self.session.add(entity)
            self.session.commit()
            return entity
        except SQLAlchemyError as e:
            self.session.rollback()
            self.logger.error(f"Error adding {self.model_class.__name__}: {e}")
            return None
    
    def update(self, entity: T) -> Optional[T]:
        """
        Update an existing entity.
        
        Args:
            entity: Entity to update
            
        Returns:
            Updated entity or None if error
        """
        try:
            self.session.merge(entity)
            self.session.commit()
            return entity
        except SQLAlchemyError as e:
            self.session.rollback()
            self.logger.error(f"Error updating {self.model_class.__name__}: {e}")
            return None
    
    def delete(self, entity: T) -> bool:
        """
        Delete an entity.
        
        Args:
            entity: Entity to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.session.delete(entity)
            self.session.commit()
            return True
        except SQLAlchemyError as e:
            self.session.rollback()
            self.logger.error(f"Error deleting {self.model_class.__name__}: {e}")
            return False
    
    def delete_by_id(self, entity_id: str) -> bool:
        """
        Delete an entity by ID.
        
        Args:
            entity_id: ID of entity to delete
            
        Returns:
            True if successful, False otherwise
        """
        entity = self.get_by_id(entity_id)
        if entity:
            return self.delete(entity)
        return False


class AbilityRepository(Repository[Ability]):
    """Repository for Ability entities."""
    
    def find_by_ability_id(self, ability_id: str) -> Optional[Ability]:
        """
        Find ability by ability_id.
        
        Args:
            ability_id: Ability ID
            
        Returns:
            Ability or None if not found
        """
        try:
            return self.session.query(Ability).filter_by(ability_id=ability_id).first()
        except SQLAlchemyError as e:
            self.logger.error(f"Error finding ability by ability_id: {e}")
            return None
    
    def find_by_tactic(self, tactic: str) -> List[Ability]:
        """
        Find abilities by tactic.
        
        Args:
            tactic: Tactic name
            
        Returns:
            List of abilities
        """
        try:
            return self.session.query(Ability).filter_by(tactic=tactic).all()
        except SQLAlchemyError as e:
            self.logger.error(f"Error finding abilities by tactic: {e}")
            return []
    
    def find_by_technique_id(self, technique_id: str) -> List[Ability]:
        """
        Find abilities by ATT&CK technique ID.
        
        Args:
            technique_id: ATT&CK technique ID
            
        Returns:
            List of abilities
        """
        try:
            return self.session.query(Ability).filter_by(technique_id=technique_id).all()
        except SQLAlchemyError as e:
            self.logger.error(f"Error finding abilities by technique_id: {e}")
            return []
    
    def find_by_plugin(self, plugin: str) -> List[Ability]:
        """
        Find abilities by plugin.
        
        Args:
            plugin: Plugin name
            
        Returns:
            List of abilities
        """
        try:
            return self.session.query(Ability).filter_by(plugin=plugin).all()
        except SQLAlchemyError as e:
            self.logger.error(f"Error finding abilities by plugin: {e}")
            return []


class AdversaryRepository(Repository[Adversary]):
    """Repository for Adversary entities."""
    
    def find_by_adversary_id(self, adversary_id: str) -> Optional[Adversary]:
        """
        Find adversary by adversary_id.
        
        Args:
            adversary_id: Adversary ID
            
        Returns:
            Adversary or None if not found
        """
        try:
            return self.session.query(Adversary).filter_by(adversary_id=adversary_id).first()
        except SQLAlchemyError as e:
            self.logger.error(f"Error finding adversary by adversary_id: {e}")
            return None
    
    def find_by_plugin(self, plugin: str) -> List[Adversary]:
        """
        Find adversaries by plugin.
        
        Args:
            plugin: Plugin name
            
        Returns:
            List of adversaries
        """
        try:
            return self.session.query(Adversary).filter_by(plugin=plugin).all()
        except SQLAlchemyError as e:
            self.logger.error(f"Error finding adversaries by plugin: {e}")
            return []


class AgentRepository(Repository[Agent]):
    """Repository for Agent entities."""
    
    def find_by_paw(self, paw: str) -> Optional[Agent]:
        """
        Find agent by paw.
        
        Args:
            paw: Agent paw
            
        Returns:
            Agent or None if not found
        """
        try:
            return self.session.query(Agent).filter_by(paw=paw).first()
        except SQLAlchemyError as e:
            self.logger.error(f"Error finding agent by paw: {e}")
            return None
    
    def find_by_platform(self, platform: str) -> List[Agent]:
        """
        Find agents by platform.
        
        Args:
            platform: Platform name
            
        Returns:
            List of agents
        """
        try:
            return self.session.query(Agent).filter_by(platform=platform).all()
        except SQLAlchemyError as e:
            self.logger.error(f"Error finding agents by platform: {e}")
            return []
    
    def find_trusted(self) -> List[Agent]:
        """
        Find trusted agents.
        
        Returns:
            List of trusted agents
        """
        try:
            return self.session.query(Agent).filter_by(trusted=True).all()
        except SQLAlchemyError as e:
            self.logger.error(f"Error finding trusted agents: {e}")
            return []


class OperationRepository(Repository[Operation]):
    """Repository for Operation entities."""
    
    def find_by_state(self, state: str) -> List[Operation]:
        """
        Find operations by state.
        
        Args:
            state: Operation state
            
        Returns:
            List of operations
        """
        try:
            return self.session.query(Operation).filter_by(state=state).all()
        except SQLAlchemyError as e:
            self.logger.error(f"Error finding operations by state: {e}")
            return []
    
    def find_by_adversary_id(self, adversary_id: str) -> List[Operation]:
        """
        Find operations by adversary ID.
        
        Args:
            adversary_id: Adversary ID
            
        Returns:
            List of operations
        """
        try:
            return self.session.query(Operation).filter_by(adversary_id=adversary_id).all()
        except SQLAlchemyError as e:
            self.logger.error(f"Error finding operations by adversary_id: {e}")
            return []
    
    def find_active(self) -> List[Operation]:
        """
        Find active operations (not finished).
        
        Returns:
            List of active operations
        """
        try:
            return self.session.query(Operation).filter(Operation.finish == None).all()
        except SQLAlchemyError as e:
            self.logger.error(f"Error finding active operations: {e}")
            return []


class LinkRepository(Repository[Link]):
    """Repository for Link entities."""
    
    def find_by_operation_id(self, operation_id: str) -> List[Link]:
        """
        Find links by operation ID.
        
        Args:
            operation_id: Operation ID
            
        Returns:
            List of links
        """
        try:
            return self.session.query(Link).filter_by(operation_id=operation_id).all()
        except SQLAlchemyError as e:
            self.logger.error(f"Error finding links by operation_id: {e}")
            return []
    
    def find_by_agent_id(self, agent_id: str) -> List[Link]:
        """
        Find links by agent ID.
        
        Args:
            agent_id: Agent ID
            
        Returns:
            List of links
        """
        try:
            return self.session.query(Link).filter_by(agent_id=agent_id).all()
        except SQLAlchemyError as e:
            self.logger.error(f"Error finding links by agent_id: {e}")
            return []
    
    def find_by_status(self, status: int) -> List[Link]:
        """
        Find links by status.
        
        Args:
            status: Link status
            
        Returns:
            List of links
        """
        try:
            return self.session.query(Link).filter_by(status=status).all()
        except SQLAlchemyError as e:
            self.logger.error(f"Error finding links by status: {e}")
            return []


class ObjectiveRepository(Repository[Objective]):
    """Repository for Objective entities."""
    
    def find_by_name(self, name: str) -> Optional[Objective]:
        """
        Find objective by name.
        
        Args:
            name: Objective name
            
        Returns:
            Objective or None if not found
        """
        try:
            return self.session.query(Objective).filter_by(name=name).first()
        except SQLAlchemyError as e:
            self.logger.error(f"Error finding objective by name: {e}")
            return None


class PluginRepository(Repository[Plugin]):
    """Repository for Plugin entities."""
    
    def find_by_name(self, name: str) -> Optional[Plugin]:
        """
        Find plugin by name.
        
        Args:
            name: Plugin name
            
        Returns:
            Plugin or None if not found
        """
        try:
            return self.session.query(Plugin).filter_by(name=name).first()
        except SQLAlchemyError as e:
            self.logger.error(f"Error finding plugin by name: {e}")
            return None
    
    def find_enabled(self) -> List[Plugin]:
        """
        Find enabled plugins.
        
        Returns:
            List of enabled plugins
        """
        try:
            return self.session.query(Plugin).filter_by(enabled=True).all()
        except SQLAlchemyError as e:
            self.logger.error(f"Error finding enabled plugins: {e}")
            return []


class SourceRepository(Repository[Source]):
    """Repository for Source entities."""
    
    def find_by_name(self, name: str) -> Optional[Source]:
        """
        Find source by name.
        
        Args:
            name: Source name
            
        Returns:
            Source or None if not found
        """
        try:
            return self.session.query(Source).filter_by(name=name).first()
        except SQLAlchemyError as e:
            self.logger.error(f"Error finding source by name: {e}")
            return None


class PlannerRepository(Repository[Planner]):
    """Repository for Planner entities."""
    
    def find_by_name(self, name: str) -> Optional[Planner]:
        """
        Find planner by name.
        
        Args:
            name: Planner name
            
        Returns:
            Planner or None if not found
        """
        try:
            return self.session.query(Planner).filter_by(name=name).first()
        except SQLAlchemyError as e:
            self.logger.error(f"Error finding planner by name: {e}")
            return None


class ScheduleRepository(Repository[Schedule]):
    """Repository for Schedule entities."""
    
    def find_by_name(self, name: str) -> Optional[Schedule]:
        """
        Find schedule by name.
        
        Args:
            name: Schedule name
            
        Returns:
            Schedule or None if not found
        """
        try:
            return self.session.query(Schedule).filter_by(name=name).first()
        except SQLAlchemyError as e:
            self.logger.error(f"Error finding schedule by name: {e}")
            return None


# Factory function to get the appropriate repository for a model class
def get_repository(session: Session, model_class: Type[T]) -> Repository[T]:
    """
    Get repository for a model class.
    
    Args:
        session: SQLAlchemy session
        model_class: Model class
        
    Returns:
        Repository for the model class
    """
    repositories = {
        Ability: AbilityRepository,
        Adversary: AdversaryRepository,
        Agent: AgentRepository,
        Operation: OperationRepository,
        Link: LinkRepository,
        Objective: ObjectiveRepository,
        Plugin: PluginRepository,
        Source: SourceRepository,
        Planner: PlannerRepository,
        Schedule: ScheduleRepository,
    }
    
    repository_class = repositories.get(model_class, Repository)
    return repository_class(session, model_class)
