"""
Migration tool for Caldera database.

This module provides tools for migrating data from the current JSON/pickle storage
to the new database system.
"""

import os
import json
import pickle
import logging
import datetime
from typing import Dict, Any, List, Optional, Union, Tuple

from sqlalchemy.orm import Session

from app.database.models import (
    Base, Ability, Executor, Parser, Requirement, Adversary, Agent,
    Operation, Link, Objective, Goal, Plugin, Source, Planner,
    Schedule, DataEncoder, Obfuscator
)
from app.database.service import DatabaseService, get_db_service
from app.utility.json_serializer import deserialize_object

logger = logging.getLogger('database_migration')

class MigrationError(Exception):
    """Exception raised for errors during migration."""
    pass

def load_json_data(file_path: str) -> Dict[str, List[Any]]:
    """
    Load data from JSON file.
    
    Args:
        file_path: Path to JSON file
        
    Returns:
        Dictionary of data
    """
    try:
        if not os.path.exists(file_path):
            logger.warning(f"JSON file not found: {file_path}")
            return {}
        
        with open(file_path, 'r') as f:
            json_str = f.read()
        
        return deserialize_object(json_str)
    except Exception as e:
        logger.error(f"Error loading JSON data from {file_path}: {e}")
        return {}

def load_pickle_data(file_path: str) -> Dict[str, List[Any]]:
    """
    Load data from pickle file.
    
    Args:
        file_path: Path to pickle file
        
    Returns:
        Dictionary of data
    """
    try:
        if not os.path.exists(file_path):
            logger.warning(f"Pickle file not found: {file_path}")
            return {}
        
        with open(file_path, 'rb') as f:
            data = pickle.load(f)
        
        return data
    except Exception as e:
        logger.error(f"Error loading pickle data from {file_path}: {e}")
        return {}

def load_data() -> Dict[str, List[Any]]:
    """
    Load data from JSON or pickle file.
    
    Returns:
        Dictionary of data
    """
    # Try to load from JSON first
    data = load_json_data('data/object_store.json')
    if data:
        logger.info("Loaded data from JSON file")
        return data
    
    # Fall back to pickle
    data = load_pickle_data('data/object_store')
    if data:
        logger.info("Loaded data from pickle file")
        return data
    
    logger.warning("No data found to migrate")
    return {}

def migrate_abilities(session: Session, abilities: List[Any]) -> Dict[str, str]:
    """
    Migrate abilities to database.
    
    Args:
        session: SQLAlchemy session
        abilities: List of ability objects
        
    Returns:
        Dictionary mapping old IDs to new IDs
    """
    id_map = {}
    
    for ability_obj in abilities:
        try:
            # Create ability
            ability = Ability(
                ability_id=ability_obj.ability_id,
                name=ability_obj.name,
                description=ability_obj.description,
                tactic=ability_obj.tactic,
                technique_id=ability_obj.technique_id,
                technique_name=ability_obj.technique_name,
                privilege=ability_obj.privilege,
                repeatable=ability_obj.repeatable,
                singleton=ability_obj.singleton,
                plugin=ability_obj.plugin,
                access=ability_obj.access
            )
            session.add(ability)
            session.flush()  # Flush to get ID
            
            # Map old ID to new ID
            id_map[ability_obj.ability_id] = ability.id
            
            # Create executors
            for executor_obj in ability_obj.executors:
                executor = Executor(
                    ability_id=ability.id,
                    name=executor_obj.name,
                    platform=executor_obj.platform,
                    command=executor_obj.command,
                    code=executor_obj.code,
                    language=executor_obj.language,
                    build_target=executor_obj.build_target,
                    timeout=executor_obj.timeout,
                    cleanup=executor_obj.cleanup
                )
                session.add(executor)
                session.flush()
                
                # Create parsers
                for parser_obj in executor_obj.parsers:
                    parser = Parser(
                        executor_id=executor.id,
                        module=parser_obj.module,
                        config=parser_obj.parserconfigs
                    )
                    session.add(parser)
            
            # Create requirements
            for req_obj in ability_obj.requirements:
                req = Requirement(
                    ability_id=ability.id,
                    module=req_obj.module,
                    relationship_match=req_obj.relationship_match
                )
                session.add(req)
            
            logger.debug(f"Migrated ability: {ability.name} ({ability.ability_id})")
        except Exception as e:
            logger.error(f"Error migrating ability {ability_obj.ability_id}: {e}")
    
    return id_map

def migrate_adversaries(session: Session, adversaries: List[Any], ability_id_map: Dict[str, str]) -> Dict[str, str]:
    """
    Migrate adversaries to database.
    
    Args:
        session: SQLAlchemy session
        adversaries: List of adversary objects
        ability_id_map: Dictionary mapping ability IDs
        
    Returns:
        Dictionary mapping old IDs to new IDs
    """
    id_map = {}
    
    for adversary_obj in adversaries:
        try:
            # Create adversary
            adversary = Adversary(
                adversary_id=adversary_obj.adversary_id,
                name=adversary_obj.name,
                description=adversary_obj.description,
                plugin=adversary_obj.plugin,
                access=adversary_obj.access
            )
            session.add(adversary)
            session.flush()
            
            # Map old ID to new ID
            id_map[adversary_obj.adversary_id] = adversary.id
            
            # Add abilities
            for ability_id in adversary_obj.atomic_ordering:
                if ability_id in ability_id_map:
                    ability = session.query(Ability).filter_by(id=ability_id_map[ability_id]).first()
                    if ability:
                        adversary.abilities.append(ability)
            
            logger.debug(f"Migrated adversary: {adversary.name} ({adversary.adversary_id})")
        except Exception as e:
            logger.error(f"Error migrating adversary {adversary_obj.adversary_id}: {e}")
    
    return id_map

def migrate_agents(session: Session, agents: List[Any]) -> Dict[str, str]:
    """
    Migrate agents to database.
    
    Args:
        session: SQLAlchemy session
        agents: List of agent objects
        
    Returns:
        Dictionary mapping old IDs to new IDs
    """
    id_map = {}
    
    for agent_obj in agents:
        try:
            # Create agent
            agent = Agent(
                paw=agent_obj.paw,
                host=agent_obj.host,
                username=agent_obj.username,
                group=agent_obj.group,
                architecture=agent_obj.architecture,
                platform=agent_obj.platform,
                location=agent_obj.location,
                pid=agent_obj.pid,
                ppid=agent_obj.ppid,
                trusted=agent_obj.trusted,
                sleep_min=agent_obj.sleep_min,
                sleep_max=agent_obj.sleep_max,
                watchdog=agent_obj.watchdog,
                contact=agent_obj.contact,
                pending_contact=agent_obj.pending_contact,
                last_seen=agent_obj.last_seen,
                last_trusted_seen=agent_obj.last_trusted_seen
            )
            session.add(agent)
            session.flush()
            
            # Map old ID to new ID
            id_map[agent_obj.paw] = agent.id
            
            logger.debug(f"Migrated agent: {agent.paw}")
        except Exception as e:
            logger.error(f"Error migrating agent {agent_obj.paw}: {e}")
    
    return id_map

def migrate_operations(session: Session, operations: List[Any], adversary_id_map: Dict[str, str], agent_id_map: Dict[str, str], ability_id_map: Dict[str, str]) -> Dict[str, str]:
    """
    Migrate operations to database.
    
    Args:
        session: SQLAlchemy session
        operations: List of operation objects
        adversary_id_map: Dictionary mapping adversary IDs
        agent_id_map: Dictionary mapping agent IDs
        ability_id_map: Dictionary mapping ability IDs
        
    Returns:
        Dictionary mapping old IDs to new IDs
    """
    id_map = {}
    
    for op_obj in operations:
        try:
            # Get adversary ID
            adversary_id = None
            if op_obj.adversary_id and op_obj.adversary_id in adversary_id_map:
                adversary_id = adversary_id_map[op_obj.adversary_id]
            
            # Create operation
            operation = Operation(
                name=op_obj.name,
                adversary_id=adversary_id,
                state=op_obj.state,
                planner=op_obj.planner,
                jitter=op_obj.jitter,
                start=op_obj.start,
                finish=op_obj.finish,
                phase=op_obj.phase,
                obfuscator=op_obj.obfuscator,
                autonomous=op_obj.autonomous,
                chain_mode=op_obj.chain_mode,
                auto_close=op_obj.auto_close,
                visibility=op_obj.visibility
            )
            session.add(operation)
            session.flush()
            
            # Map old ID to new ID
            id_map[op_obj.id] = operation.id
            
            # Add agents
            for agent_obj in op_obj.agents:
                if agent_obj.paw in agent_id_map:
                    agent = session.query(Agent).filter_by(id=agent_id_map[agent_obj.paw]).first()
                    if agent:
                        operation.agents.append(agent)
            
            # Add abilities
            for ability_id in getattr(op_obj, 'abilities', []):
                if ability_id in ability_id_map:
                    ability = session.query(Ability).filter_by(id=ability_id_map[ability_id]).first()
                    if ability:
                        operation.abilities.append(ability)
            
            logger.debug(f"Migrated operation: {operation.name} ({operation.id})")
        except Exception as e:
            logger.error(f"Error migrating operation {op_obj.id}: {e}")
    
    return id_map

def migrate_links(session: Session, operations: List[Any], operation_id_map: Dict[str, str], agent_id_map: Dict[str, str], ability_id_map: Dict[str, str]):
    """
    Migrate links to database.
    
    Args:
        session: SQLAlchemy session
        operations: List of operation objects
        operation_id_map: Dictionary mapping operation IDs
        agent_id_map: Dictionary mapping agent IDs
        ability_id_map: Dictionary mapping ability IDs
    """
    for op_obj in operations:
        try:
            if op_obj.id not in operation_id_map:
                continue
                
            operation_id = operation_id_map[op_obj.id]
            
            # Migrate links
            for link_obj in op_obj.chain:
                try:
                    # Get agent ID
                    agent_id = None
                    if link_obj.paw in agent_id_map:
                        agent_id = agent_id_map[link_obj.paw]
                    
                    # Get ability ID
                    ability_id = None
                    if link_obj.ability.ability_id in ability_id_map:
                        ability_id = ability_id_map[link_obj.ability.ability_id]
                    
                    if not agent_id or not ability_id:
                        continue
                    
                    # Create link
                    link = Link(
                        operation_id=operation_id,
                        agent_id=agent_id,
                        ability_id=ability_id,
                        command=link_obj.command,
                        status=link_obj.status,
                        score=link_obj.score,
                        jitter=link_obj.jitter,
                        cleanup=link_obj.cleanup,
                        created_at=link_obj.created,
                        decide=link_obj.decide,
                        collect=link_obj.collect,
                        finish=link_obj.finish
                    )
                    session.add(link)
                    
                    logger.debug(f"Migrated link: {link.id}")
                except Exception as e:
                    logger.error(f"Error migrating link: {e}")
        except Exception as e:
            logger.error(f"Error migrating links for operation {op_obj.id}: {e}")

def migrate_objectives(session: Session, objectives: List[Any]) -> Dict[str, str]:
    """
    Migrate objectives to database.
    
    Args:
        session: SQLAlchemy session
        objectives: List of objective objects
        
    Returns:
        Dictionary mapping old IDs to new IDs
    """
    id_map = {}
    
    for obj_obj in objectives:
        try:
            # Create objective
            objective = Objective(
                id=obj_obj.id,
                name=obj_obj.name,
                description=obj_obj.description,
                plugin=obj_obj.plugin,
                access=obj_obj.access
            )
            session.add(objective)
            session.flush()
            
            # Map old ID to new ID
            id_map[obj_obj.id] = objective.id
            
            # Create goals
            for goal_obj in obj_obj.goals:
                goal = Goal(
                    objective_id=objective.id,
                    target=goal_obj.target,
                    value=goal_obj.value,
                    count=goal_obj.count,
                    achieved=goal_obj.achieved
                )
                session.add(goal)
            
            logger.debug(f"Migrated objective: {objective.name} ({objective.id})")
        except Exception as e:
            logger.error(f"Error migrating objective {obj_obj.id}: {e}")
    
    return id_map

def migrate_plugins(session: Session, plugins: List[Any]) -> Dict[str, str]:
    """
    Migrate plugins to database.
    
    Args:
        session: SQLAlchemy session
        plugins: List of plugin objects
        
    Returns:
        Dictionary mapping old IDs to new IDs
    """
    id_map = {}
    
    for plugin_obj in plugins:
        try:
            # Create plugin
            plugin = Plugin(
                name=plugin_obj.name,
                enabled=plugin_obj.enabled,
                description=getattr(plugin_obj, 'description', None),
                address=getattr(plugin_obj, 'address', None),
                data_dir=plugin_obj.data_dir,
                access=getattr(plugin_obj, 'access', None)
            )
            session.add(plugin)
            session.flush()
            
            # Map old ID to new ID
            id_map[plugin_obj.name] = plugin.id
            
            logger.debug(f"Migrated plugin: {plugin.name}")
        except Exception as e:
            logger.error(f"Error migrating plugin {plugin_obj.name}: {e}")
    
    return id_map

def migrate_sources(session: Session, sources: List[Any]) -> Dict[str, str]:
    """
    Migrate sources to database.
    
    Args:
        session: SQLAlchemy session
        sources: List of source objects
        
    Returns:
        Dictionary mapping old IDs to new IDs
    """
    id_map = {}
    
    for source_obj in sources:
        try:
            # Create source
            source = Source(
                id=source_obj.id,
                name=source_obj.name,
                plugin=source_obj.plugin,
                facts=source_obj.facts
            )
            session.add(source)
            session.flush()
            
            # Map old ID to new ID
            id_map[source_obj.id] = source.id
            
            logger.debug(f"Migrated source: {source.name} ({source.id})")
        except Exception as e:
            logger.error(f"Error migrating source {source_obj.id}: {e}")
    
    return id_map

def migrate_planners(session: Session, planners: List[Any]) -> Dict[str, str]:
    """
    Migrate planners to database.
    
    Args:
        session: SQLAlchemy session
        planners: List of planner objects
        
    Returns:
        Dictionary mapping old IDs to new IDs
    """
    id_map = {}
    
    for planner_obj in planners:
        try:
            # Create planner
            planner = Planner(
                id=planner_obj.id,
                name=planner_obj.name,
                module=planner_obj.module,
                description=planner_obj.description,
                stopping_conditions=planner_obj.stopping_conditions,
                params=planner_obj.params,
                allow_repeats=planner_obj.allow_repeats
            )
            session.add(planner)
            session.flush()
            
            # Map old ID to new ID
            id_map[planner_obj.id] = planner.id
            
            logger.debug(f"Migrated planner: {planner.name} ({planner.id})")
        except Exception as e:
            logger.error(f"Error migrating planner {planner_obj.id}: {e}")
    
    return id_map

def migrate_schedules(session: Session, schedules: List[Any]) -> Dict[str, str]:
    """
    Migrate schedules to database.
    
    Args:
        session: SQLAlchemy session
        schedules: List of schedule objects
        
    Returns:
        Dictionary mapping old IDs to new IDs
    """
    id_map = {}
    
    for schedule_obj in schedules:
        try:
            # Create schedule
            schedule = Schedule(
                id=schedule_obj.id,
                name=schedule_obj.name,
                schedule=schedule_obj.schedule,
                task_id=schedule_obj.task_id
            )
            session.add(schedule)
            session.flush()
            
            # Map old ID to new ID
            id_map[schedule_obj.id] = schedule.id
            
            logger.debug(f"Migrated schedule: {schedule.name} ({schedule.id})")
        except Exception as e:
            logger.error(f"Error migrating schedule {schedule_obj.id}: {e}")
    
    return id_map

def migrate_data_encoders(session: Session, data_encoders: List[Any]) -> Dict[str, str]:
    """
    Migrate data encoders to database.
    
    Args:
        session: SQLAlchemy session
        data_encoders: List of data encoder objects
        
    Returns:
        Dictionary mapping old IDs to new IDs
    """
    id_map = {}
    
    for encoder_obj in data_encoders:
        try:
            # Create data encoder
            encoder = DataEncoder(
                id=encoder_obj.id,
                name=encoder_obj.name,
                description=encoder_obj.description
            )
            session.add(encoder)
            session.flush()
            
            # Map old ID to new ID
            id_map[encoder_obj.id] = encoder.id
            
            logger.debug(f"Migrated data encoder: {encoder.name} ({encoder.id})")
        except Exception as e:
            logger.error(f"Error migrating data encoder {encoder_obj.id}: {e}")
    
    return id_map

def migrate_obfuscators(session: Session, obfuscators: List[Any]) -> Dict[str, str]:
    """
    Migrate obfuscators to database.
    
    Args:
        session: SQLAlchemy session
        obfuscators: List of obfuscator objects
        
    Returns:
        Dictionary mapping old IDs to new IDs
    """
    id_map = {}
    
    for obfuscator_obj in obfuscators:
        try:
            # Create obfuscator
            obfuscator = Obfuscator(
                id=obfuscator_obj.id,
                name=obfuscator_obj.name,
                description=obfuscator_obj.description
            )
            session.add(obfuscator)
            session.flush()
            
            # Map old ID to new ID
            id_map[obfuscator_obj.id] = obfuscator.id
            
            logger.debug(f"Migrated obfuscator: {obfuscator.name} ({obfuscator.id})")
        except Exception as e:
            logger.error(f"Error migrating obfuscator {obfuscator_obj.id}: {e}")
    
    return id_map

def migrate_all_data(db_service: DatabaseService = None) -> bool:
    """
    Migrate all data from JSON/pickle to database.
    
    Args:
        db_service: Database service (optional)
        
    Returns:
        True if migration was successful, False otherwise
    """
    if db_service is None:
        db_service = get_db_service()
    
    try:
        # Load data
        data = load_data()
        if not data:
            logger.warning("No data to migrate")
            return False
        
        # Create tables
        db_service.create_tables()
        
        # Migrate data
        with db_service.session() as session:
            # Migrate in order of dependencies
            ability_id_map = migrate_abilities(session, data.get('abilities', []))
            adversary_id_map = migrate_adversaries(session, data.get('adversaries', []), ability_id_map)
            agent_id_map = migrate_agents(session, data.get('agents', []))
            operation_id_map = migrate_operations(session, data.get('operations', []), adversary_id_map, agent_id_map, ability_id_map)
            migrate_links(session, data.get('operations', []), operation_id_map, agent_id_map, ability_id_map)
            migrate_objectives(session, data.get('objectives', []))
            migrate_plugins(session, data.get('plugins', []))
            migrate_sources(session, data.get('sources', []))
            migrate_planners(session, data.get('planners', []))
            migrate_schedules(session, data.get('schedules', []))
            migrate_data_encoders(session, data.get('data_encoders', []))
            migrate_obfuscators(session, data.get('obfuscators', []))
        
        logger.info("Migration completed successfully")
        return True
    except Exception as e:
        logger.error(f"Error during migration: {e}")
        return False

def main():
    """Main function for running migration from command line."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Migrate Caldera data to database')
    parser.add_argument('--connection-string', help='Database connection string')
    parser.add_argument('--log-level', default='INFO', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                        help='Logging level')
    args = parser.parse_args()
    
    # Configure logging
    logging.basicConfig(level=getattr(logging, args.log_level),
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Create database service
    db_service = DatabaseService(args.connection_string)
    
    # Migrate data
    success = migrate_all_data(db_service)
    
    if success:
        print("Migration completed successfully")
    else:
        print("Migration failed")
        return 1
    
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main())
