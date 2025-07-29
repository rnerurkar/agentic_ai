"""
Base Agent Classes for Google ADK (Agent Development Kit) Framework

This module provides the foundational classes and patterns for building AI agents using Google's
Agent Development Kit (ADK). It demonstrates core concepts that every ADK developer should understand.

Key ADK Concepts for Newcomers:
- Agents are autonomous software components that react to events
- They follow an event-driven architecture pattern
- Each agent has a specific responsibility in the workflow
- Agents communicate through pub/sub messaging
- Human verification can be requested at any stage

Architecture Pattern:
This follows the Template Method pattern - the base Agent class defines the framework
structure, and specific agent implementations inherit and customize behavior.

For ADK Beginners:
Google ADK is designed for building scalable, event-driven AI workflows where multiple
agents collaborate to solve complex problems. Each agent is specialized for a specific
task and can run independently or as part of a larger workflow.
"""

# Core Python libraries for asynchronous programming and abstract base classes
import asyncio  # For handling asynchronous operations (essential for event-driven agents)
from abc import ABC, abstractmethod  # For defining abstract base classes and interfaces
from typing import Dict, Any, List, Optional  # For type hints and better code documentation

# Import mock services for development and testing
# In production ADK, these would be replaced with actual Google Cloud services
from mock_services import MockMonitoring


class Agent:
    """
    Base ADK Agent class for all intelligent agents in the EnGen workflow
    
    This class provides the fundamental structure that all ADK agents should follow:
    - Event-driven architecture for reactive behavior
    - Monitoring and observability integration
    - Human verification capabilities
    - Standardized error handling and logging
    
    Key ADK Principles Demonstrated:
    1. Event-Driven Design: Agents react to events rather than polling
    2. Loose Coupling: Agents communicate through events, not direct calls
    3. Human-in-the-Loop: Critical decisions can be escalated to humans
    4. Observability: All agent actions are monitored and logged
    5. Resilience: Graceful error handling and recovery
    
    For ADK Newcomers:
    Think of agents as specialized workers in a factory. Each worker (agent) has
    a specific job, waits for work (events) to arrive, processes that work,
    and then sends the results to the next worker in the assembly line.
    
    Example Agent Types in ADK:
    - Validation agents (check input quality)
    - Processing agents (transform data)
    - Decision agents (make intelligent choices)
    - Integration agents (connect to external systems)
    """
    
    def __init__(self):
        """
        Initialize the base agent with essential ADK capabilities
        
        Every ADK agent needs certain core capabilities:
        - Monitoring for observability and debugging
        - Event handling for reactive behavior
        - Error handling for resilience
        - Communication channels for collaboration
        
        In production ADK environments, this would also include:
        - Authentication and authorization
        - Rate limiting and throttling
        - Metrics collection and reporting
        - Health check endpoints
        """
        # Initialize monitoring for observability
        # This allows tracking agent performance, errors, and behavior
        self.monitoring = MockMonitoring()
        
        # Agent metadata for identification and debugging
        self.agent_id = self.__class__.__name__
        self.version = "1.0.0"
        self.status = "initialized"
    
    async def on_event(self, event):
        """
        Default event handler for incoming events
        
        This is the core method of the event-driven architecture in ADK.
        Every agent receives events and decides how to process them.
        
        Event-Driven Architecture in ADK:
        - Events are messages that trigger agent actions
        - Events can come from user interactions, system changes, or other agents
        - Agents process events asynchronously for better performance
        - Events contain all context needed for processing
        
        Common Event Types in ADK:
        - User input events (uploaded files, text input)
        - System events (file changes, database updates)
        - Agent events (workflow stage completions)
        - Timer events (scheduled processing)
        
        Args:
            event: Event object containing trigger information and context
                  Typically includes: event_type, data, timestamp, source
                  
        For ADK Beginners:
        Think of events like mail delivery - when mail arrives at your house,
        you check what type it is and decide what to do with it. Agents work
        the same way with digital events.
        """
        # Default implementation does nothing - subclasses override this
        # Log the event for debugging and monitoring
        await self.monitoring.log_event(f"Agent {self.agent_id} received event: {event}")
        pass

    async def request_human_verification(self, stage: str, context: dict):
        """
        Request human verification for critical decisions or quality checks
        
        Human-in-the-Loop is a core ADK pattern where humans provide:
        - Quality assurance for AI-generated content
        - Business decisions that require judgment
        - Exception handling for edge cases
        - Final approval for critical operations
        
        This method demonstrates how ADK agents can escalate decisions to humans
        when automated processing isn't sufficient or when human oversight is required.
        
        ADK Human Verification Patterns:
        1. Checkpoint Pattern: Stop workflow for human review
        2. Parallel Pattern: Continue workflow while human reviews
        3. Exception Pattern: Only involve humans for errors or edge cases
        4. Approval Pattern: Require human sign-off for actions
        
        Args:
            stage (str): The workflow stage requesting verification
                        Examples: "diagram_validation", "document_approval", "deployment_sign_off"
            context (dict): All relevant information for human decision-making
                           Should include: data to review, options available, risk level
                           
        For ADK Beginners:
        This is like having a supervisor review your work before it goes to the customer.
        The AI agent does the initial work, but a human checks it for quality and correctness.
        """
        from mock_services import pubsub
        import json
        
        # Create a structured verification request
        verification_request = {
            "stage": stage,
            "context": context,
            "agent_id": self.agent_id,
            "timestamp": asyncio.get_event_loop().time(),
            "priority": context.get("priority", "normal"),
            "estimated_review_time": context.get("review_time_minutes", 15)
        }
        
        # Publish to human verification topic
        # In production ADK, this would integrate with workflow management systems
        await pubsub.publish(
            "projects/engen-project/topics/human-verification",
            data=json.dumps(verification_request).encode()
        )
        
        # Log the verification request for tracking
        await self.monitoring.log_event(
            f"Human verification requested for {stage} by {self.agent_id}"
        )
