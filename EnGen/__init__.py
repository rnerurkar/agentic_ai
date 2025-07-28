"""
EnGen ADK Agents Package
Complete modular implementation of the EnGen workflow using Google's Agent Development Kit (ADK)
"""

try:
    # Try relative imports first (when package is properly installed)
    from .base_agent import Agent
    from .diagram_validator_agent import DiagramValidatorAgent
    from .document_generation_agent import DocumentGenerationAgent
    from .component_specification_agent import ComponentSpecificationAgent
    from .artifact_generation_agent import ArtifactGenerationAgent
    from .human_verifier_agent import HumanVerifierAgent
    from .workflow_orchestrator import WorkflowOrchestrator
except ImportError:
    # Fall back to absolute imports (when running from within directory)
    from base_agent import Agent
    from diagram_validator_agent import DiagramValidatorAgent
    from document_generation_agent import DocumentGenerationAgent
    from component_specification_agent import ComponentSpecificationAgent
    from artifact_generation_agent import ArtifactGenerationAgent
    from human_verifier_agent import HumanVerifierAgent
    from workflow_orchestrator import WorkflowOrchestrator

__version__ = "1.0.0"
__author__ = "EnGen Team"
__description__ = "Modular ADK agents for enterprise pattern generation workflow"

# Export all agent classes
__all__ = [
    "Agent",
    "DiagramValidatorAgent", 
    "DocumentGenerationAgent",
    "ComponentSpecificationAgent",
    "ArtifactGenerationAgent",
    "HumanVerifierAgent",
    "WorkflowOrchestrator"
]
