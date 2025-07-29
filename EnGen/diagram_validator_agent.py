"""
Diagram Validator Agent - Stage 1 of EnGen Workflow

This agent demonstrates core ADK (Agent Development Kit) patterns for building intelligent
validation systems. It showcases how to create AI agents that process visual input using
multimodal models and make quality decisions with human oversight.

Key ADK Learning Objectives:
- Event-driven agent architecture responding to cloud storage events
- Integration with Google's Vertex AI for computer vision tasks
- Human-in-the-loop validation patterns for quality assurance
- Pub/Sub messaging for agent communication
- Error handling and monitoring in distributed AI systems

For ADK Newcomers:
This agent acts as a "quality inspector" in an AI assembly line. When someone uploads
a diagram, this agent automatically checks if it matches known patterns and decides
whether it's good enough to proceed to the next stage of processing.

Real-World Applications:
- Document processing pipelines (check if documents are readable)
- Manufacturing quality control (inspect products for defects)
- Content moderation (validate uploaded images meet guidelines)
- Medical imaging analysis (initial screening of scans)
"""

# Standard library imports for data handling
import json  # For working with structured data and API responses
import time  # For timestamps and timing operations
import asyncio  # For asynchronous programming and event handling
from typing import Dict, Any, List, Optional  # Type hints for better code documentation

# Local imports for ADK framework and mock services
from base_agent import Agent  # Our base ADK agent class with common functionality
from mock_services import storage, vertexai, pubsub  # Mock cloud services for development


class DiagramValidatorAgent(Agent):
    """
    Stage 1 Agent: Validates uploaded diagrams using multimodal AI vision models
    
    This agent demonstrates several important ADK patterns:
    
    1. **Event-Driven Architecture**: Responds to Google Cloud Storage upload events
    2. **AI Model Integration**: Uses Vertex AI's Gemini Vision for image analysis
    3. **Quality Gates**: Implements scoring thresholds for automated decisions
    4. **Human Oversight**: Escalates decisions to humans when needed
    5. **State Management**: Stores results for downstream processing
    
    Workflow Process:
    ```
    Upload Event → Validate Diagram → Score Assessment → Human Review → Next Stage
    ```
    
    ADK Design Patterns Demonstrated:
    - **Observer Pattern**: Reacts to storage events
    - **Strategy Pattern**: Different validation strategies based on diagram type
    - **Chain of Responsibility**: Passes validated diagrams to next stage
    - **Human-in-the-Loop**: Critical quality decisions involve human reviewers
    
    For ADK Beginners:
    Think of this like a smart security guard at a building entrance. When someone
    tries to enter (upload a diagram), the guard (agent) checks their credentials
    (validates the diagram) and decides whether to let them in (approve for processing)
    or ask for additional verification (human review).
    """
    
    def __init__(self):
        """
        Initialize the Diagram Validator Agent with ADK best practices
        
        ADK Initialization Pattern:
        - Call parent constructor for base functionality
        - Set up communication channels (pub/sub topics)
        - Configure service connections
        - Initialize any ML models or resources
        
        In production ADK environments, this would also include:
        - Authentication setup for Google Cloud services
        - Model loading and warm-up
        - Configuration from environment variables
        - Health check endpoint registration
        """
        # Initialize base agent capabilities (monitoring, event handling, etc.)
        super().__init__()
        
        # Set up pub/sub communication for downstream stages
        # This is how agents communicate in ADK's event-driven architecture
        self.publisher = pubsub
        self.topic_path = "projects/engen-project/topics/validated-diagrams"
        
        # Configuration for validation scoring
        self.approval_threshold = 80  # Minimum score for automatic approval
        self.max_reference_patterns = 65  # Number of reference diagrams to compare against
        
        # Update agent status
        self.status = "ready_for_validation"

    async def on_gcs_upload(self, event):
        """
        Event handler for Google Cloud Storage upload events
        
        This method demonstrates the core ADK event-driven pattern:
        1. Receive event notification
        2. Extract relevant information
        3. Process the data
        4. Make decisions
        5. Trigger next steps
        
        Event-Driven Benefits in ADK:
        - **Scalability**: Agents only activate when needed
        - **Resilience**: Failed events can be retried
        - **Loose Coupling**: Agents don't need to know about each other
        - **Real-time Processing**: Immediate response to changes
        
        Args:
            event (dict): GCS event containing:
                - bucket: Storage bucket name
                - name: File path/name
                - timeCreated: Upload timestamp
                - contentType: File MIME type
                
        For ADK Beginners:
        This is like having a doorbell that automatically notifies you when
        someone arrives. The event tells you who arrived (file info) and
        when (timestamp), so you can decide what to do next.
        """
        try:
            # === STAGE 1, STEP 1: PROCESS UPLOAD EVENT ===
            # Extract file information from the event
            bucket = event['bucket']
            file_path = event['name']
            
            # Log the processing start for monitoring
            await self.monitoring.log_event(f"Processing diagram upload: {file_path}")
            
            # Read the uploaded diagram from cloud storage
            # In ADK, agents often work with cloud-native storage
            diagram = storage.read_file(bucket, file_path)

            # === STAGE 1, STEP 2: AI-POWERED VALIDATION ===
            # Use multimodal AI to validate the diagram
            validation_result = await self.validate_diagram(diagram)
            
            # Log validation results for debugging and analytics
            await self.monitoring.log_event(
                f"Validation completed for {file_path}: score={validation_result['score']}"
            )

            # === STAGE 1, STEP 3: DECISION LOGIC ===
            # Apply business rules to determine next steps
            if validation_result['score'] >= self.approval_threshold:
                # Diagram meets quality standards - proceed with processing
                
                # Generate detailed description using AI
                description = await self.generate_description(diagram, validation_result)

                # Store validated results for downstream processing
                # This demonstrates ADK's stateful processing pattern
                output_path = f"validated/{file_path}.json"
                validation_data = {
                    "original": file_path,
                    "validation": validation_result,
                    "description": description,
                    "stage": "validated",
                    "timestamp": event.get('timeCreated'),
                    "agent_version": self.version
                }
                
                storage.write_file("engen-diagrams", output_path, json.dumps(validation_data))

                # === STAGE 1, STEP 4: HUMAN VERIFICATION ===
                # Implement human-in-the-loop pattern for quality assurance
                await self.request_human_verification("diagram_validation", {
                    "diagram": file_path,
                    "validation": validation_result,
                    "description": description,
                    "priority": "normal",
                    "review_time_minutes": 5
                })
                
                # Publish success event to trigger next stage
                await self._publish_validation_success(validation_data)
                
            else:
                # Diagram doesn't meet quality standards - handle rejection
                await self.handle_rejection(validation_result, file_path)

        except Exception as e:
            # ADK error handling pattern: log detailed errors for debugging
            error_message = f"Validation failed for {event.get('name', 'unknown')}: {str(e)}"
            await self.monitoring.log_error(error_message)
            
            # In production ADK, you might also:
            # - Send alerts to operations team
            # - Retry with different parameters
            # - Route to manual processing queue

    async def validate_diagram(self, diagram: bytes) -> dict:
        """
        AI-powered diagram validation using Gemini Vision multimodal model
        
        This method demonstrates key ADK patterns for AI model integration:
        1. **Reference Data Pattern**: Compare against known good examples
        2. **Prompt Engineering**: Structured prompts for consistent results
        3. **Model Configuration**: Optimized parameters for validation tasks
        4. **Error Handling**: Graceful failure for model issues
        
        Validation Process:
        1. Load reference pattern library (65 validated diagrams)
        2. Use Gemini Vision to compare uploaded diagram against references
        3. Generate similarity scores and identify pattern matches
        4. Return structured validation results
        
        Args:
            diagram (bytes): Binary image data of the uploaded diagram
            
        Returns:
            dict: Validation results containing:
                - score: Overall quality score (0-100)
                - pattern_matches: List of similar reference patterns
                - confidence: Model confidence in the assessment
                - recommendations: Suggestions for improvement
                
        For ADK Beginners:
        This is like having an expert art critic who has memorized thousands of
        paintings. When you show them a new painting, they can instantly tell
        you how similar it is to known masterpieces and rate its quality.
        """
        # Load reference pattern library for comparison
        # This demonstrates ADK's pattern of using reference data for validation
        reference_diagrams = []
        for i in range(1, self.max_reference_patterns + 1):
            try:
                ref_diagram = storage.read_file("reference-patterns", f"pattern_{i}.png")
                reference_diagrams.append(ref_diagram)
            except Exception as e:
                # Handle missing reference patterns gracefully
                await self.monitoring.log_event(f"Reference pattern {i} not found: {e}")

        # Load validation prompt template
        # Prompt engineering is crucial for consistent AI model behavior
        validation_prompt = storage.read_file("prompts", "diagram_validation_prompt.txt").decode()

        # Call Vertex AI Gemini Vision model for image analysis
        # This demonstrates ADK's integration with Google's multimodal AI
        validation_result = vertexai.analyze_image(
            model="gemini-1.5-pro-vision",
            image=diagram,
            prompt=validation_prompt,
            reference_images=reference_diagrams,
            params={
                "temperature": 0.0,  # Deterministic results for validation
                "max_output_tokens": 1024,  # Sufficient for detailed analysis
                "safety_settings": "high"  # Strict safety filtering
            }
        )
        
        return validation_result

    async def generate_description(self, diagram: bytes, validation: dict) -> str:
        """
        Generate human-readable description of the validated diagram
        
        This method shows how ADK agents can chain multiple AI models:
        1. First model validates the diagram (Gemini Vision)
        2. Second model generates description (Claude 3.5)
        3. Results are combined for rich, multimodal understanding
        
        Model Chaining Benefits in ADK:
        - **Specialization**: Each model optimized for specific tasks
        - **Redundancy**: Multiple perspectives improve accuracy
        - **Rich Output**: Combine different model strengths
        
        Args:
            diagram (bytes): Original diagram image data
            validation (dict): Results from the validation step
            
        Returns:
            str: Human-readable description of the diagram and its patterns
            
        For ADK Beginners:
        This is like having a specialist explain what the first expert found.
        The first AI tells you if the diagram is good, the second AI explains
        what makes it good in terms humans can understand.
        """
        # Load description generation prompt template
        prompt_template = storage.read_file("prompts", "description_prompt.txt").decode()
        
        # Format prompt with validation context
        # This demonstrates prompt engineering with dynamic content
        formatted_prompt = prompt_template.format(
            validation=json.dumps(validation, indent=2),
            score=validation.get('score', 0),
            patterns=validation.get('pattern_matches', [])
        )
        
        # Use Claude 3.5 for natural language generation
        # Different models excel at different tasks in ADK workflows
        description = vertexai.generate_text(
            model="claude-3.5-sonnet@vertexai",
            prompt=formatted_prompt,
            image=diagram,  # Include image for visual context
            params={
                "max_tokens": 4096,  # Allow for detailed descriptions
                "temperature": 0.3   # Slightly creative but consistent
            }
        )
        
        return description

    async def handle_rejection(self, validation_result: dict, file_path: str):
        """
        Handle diagrams that don't meet validation criteria
        
        This method demonstrates ADK's error handling and remediation patterns:
        1. **Graceful Degradation**: Don't crash, handle failures elegantly
        2. **User Feedback**: Provide actionable information for improvement
        3. **Alternative Paths**: Offer manual review or resubmission options
        4. **Analytics**: Track rejection patterns for system improvement
        
        ADK Failure Handling Strategies:
        - **Immediate Feedback**: Tell users what went wrong
        - **Suggested Actions**: Provide specific improvement steps
        - **Escalation Paths**: Route to human experts when needed
        - **Learning Loop**: Use failures to improve the system
        
        Args:
            validation_result (dict): Details about why validation failed
            file_path (str): Path to the rejected diagram file
            
        For ADK Beginners:
        This is like a helpful teacher who doesn't just give you a failing grade,
        but explains what you did wrong and how to improve for next time.
        """
        # Log rejection for analytics and system improvement
        rejection_details = {
            "file_path": file_path,
            "score": validation_result.get('score', 0),
            "threshold": self.approval_threshold,
            "reasons": validation_result.get('rejection_reasons', []),
            "timestamp": time.time()
        }
        
        await self.monitoring.log_event(f"Diagram rejected: {json.dumps(rejection_details)}")
        
        # Store rejection details for user feedback
        rejection_report = {
            "status": "rejected",
            "score": validation_result['score'],
            "threshold_required": self.approval_threshold,
            "feedback": validation_result.get('feedback', 'Diagram does not match known patterns'),
            "suggestions": [
                "Ensure diagram follows standard notation",
                "Check that all elements are clearly visible",
                "Verify diagram completeness",
                "Consider using reference patterns as examples"
            ],
            "next_steps": "Please revise and resubmit, or request manual review"
        }
        
        # Store rejection report for user access
        output_path = f"rejected/{file_path}.json"
        storage.write_file("engen-diagrams", output_path, json.dumps(rejection_report))
        
        # Optional: Request manual review for borderline cases
        if validation_result['score'] >= (self.approval_threshold - 10):
            await self.request_human_verification("manual_review", {
                "file_path": file_path,
                "validation_result": validation_result,
                "reason": "borderline_score",
                "priority": "low"
            })

    async def on_human_approval(self, event):
        """
        Handle human verification results for validated diagrams
        
        This method completes the human-in-the-loop workflow by processing
        the human reviewer's decision and triggering appropriate next steps.
        
        Human-in-the-Loop Completion Patterns in ADK:
        1. **Decision Integration**: Incorporate human judgment into workflow
        2. **Audit Trail**: Track all human decisions for compliance
        3. **Workflow Continuation**: Seamlessly resume automated processing
        4. **Feedback Loop**: Use human decisions to improve AI models
        
        Args:
            event (dict): Human verification event containing:
                - approved: Boolean decision from human reviewer
                - context: Original validation context
                - reviewer_id: Identity of human reviewer
                - comments: Optional reviewer feedback
                
        For ADK Beginners:
        This is like getting your homework back from the teacher with their grade
        and comments, then knowing what to do next based on whether you passed.
        """
        if event.get('approved', False):
            # Human approved the validation - proceed to next stage
            await self.monitoring.log_event(
                f"Human approval received for diagram validation: {event.get('context', {}).get('diagram')}"
            )
            
            # Publish to next stage topic to trigger document generation
            await self._publish_validation_success(event['context'])
            
        else:
            # Human rejected the validation - handle as rejection
            await self.monitoring.log_event(
                f"Human rejection received for diagram validation: {event.get('context', {}).get('diagram')}"
            )
            
            # Store human feedback for learning
            feedback_data = {
                "human_decision": "rejected",
                "ai_score": event.get('context', {}).get('validation', {}).get('score'),
                "human_feedback": event.get('comments', ''),
                "reviewer_id": event.get('reviewer_id'),
                "timestamp": time.time()
            }
            
            # This data can be used to retrain and improve the AI model
            storage.write_file(
                "feedback-data", 
                f"human_feedback_{event.get('context', {}).get('diagram', 'unknown')}.json",
                json.dumps(feedback_data)
            )

    async def _publish_validation_success(self, validation_data: dict):
        """
        Publish successful validation to trigger next workflow stage
        
        This helper method demonstrates ADK's event-driven communication pattern
        for triggering downstream processing stages.
        
        Args:
            validation_data (dict): Complete validation results to pass forward
        """
        try:
            await self.publisher.publish(
                self.topic_path,
                data=json.dumps(validation_data).encode()
            )
            
            await self.monitoring.log_event(
                f"Published validation success for {validation_data.get('original')}"
            )
            
        except Exception as e:
            await self.monitoring.log_error(
                f"Failed to publish validation success: {str(e)}"
            )
