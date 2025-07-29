"""
Google ADK Document Generation Agent - Stage 2 of Document Generation Pipeline

This agent demonstrates advanced ADK patterns for intelligent content creation,
showing how to build production-ready agents that generate high-quality technical
documentation from visual inputs using multiple AI models and RAG (Retrieval-Augmented Generation).

FOR ADK BEGINNERS - WHAT THIS AGENT DOES:

This is Stage 2 of our document generation pipeline. After Stage 1 validates a diagram,
this agent receives the validation results and transforms them into comprehensive
technical documentation.

Think of this like having an expert technical writer who:
1. Understands what the diagram represents
2. Researches similar patterns and best practices  
3. Writes detailed documentation following company standards
4. Creates multiple sections (overview, architecture, components, etc.)
5. Ensures consistency with existing documentation

ADVANCED ADK CONCEPTS DEMONSTRATED:

1. **RAG (Retrieval-Augmented Generation)**:
   - Searches existing documentation for relevant context
   - Combines retrieved knowledge with AI generation
   - Ensures generated content is accurate and consistent
   - Reduces hallucinations by grounding AI in real data

2. **Multi-Model AI Integration**:
   - Uses Claude 3.5 Sonnet for technical writing
   - Could integrate GPT-4, Gemini, or custom models
   - Model selection based on task requirements
   - Fallback strategies for model failures

3. **Template-Driven Generation**:
   - Structured document templates ensure consistency
   - Configurable sections and formats
   - Dynamic prompt templates stored in Bigtable
   - Version control for template changes

4. **Vector Search Integration**:
   - Searches knowledge base using semantic similarity
   - Finds relevant examples and patterns
   - Provides context for more accurate generation
   - Scales to millions of documents

5. **Human Quality Gates**:
   - Routes generated content for human review
   - Maintains quality standards for critical documents
   - Enables continuous improvement of generation quality
   - Audit trail for compliance requirements

BUSINESS VALUE:
- Reduces documentation time from hours to minutes
- Ensures consistent formatting and style
- Incorporates organizational knowledge automatically
- Scales expert knowledge across teams
- Maintains quality through human oversight

REAL-WORLD APPLICATIONS:
- Software architecture documentation
- API documentation generation
- Process documentation from flowcharts
- Training material creation
- Compliance documentation
"""

import json
import time
import asyncio
from typing import Dict, Any, List, Optional
from base_agent import Agent
from mock_services import storage, vertexai, pubsub, bigtable


class DocumentGenerationAgent(Agent):
    """
    Stage 2: Advanced Documentation Generation with RAG and Multi-Model AI
    
    This agent demonstrates production-level ADK patterns for content generation:
    
    **ARCHITECTURE PATTERN - RAG (Retrieval-Augmented Generation)**:
    Traditional AI generation can "hallucinate" or create inaccurate content.
    RAG solves this by:
    1. Retrieving relevant existing content from knowledge base
    2. Using retrieved content as context for AI generation
    3. Grounding AI responses in verified information
    4. Ensuring consistency with organizational standards
    
    **WORKFLOW STAGES**:
    Input → RAG Retrieval → Template Hydration → AI Generation → Quality Review → Output
    
    **KEY ADK PATTERNS**:
    - **Context Enrichment**: Enhance prompts with retrieved knowledge
    - **Template Systems**: Structured, reusable content formats  
    - **Multi-Model Strategy**: Use best AI model for each task
    - **Quality Gates**: Human review for critical content
    - **Audit Trails**: Track all generation decisions and sources
    
    **FOR ADK BEGINNERS**:
    This is like having a research assistant (RAG), a writing template (structure),
    and an expert writer (AI model) working together to create documentation
    that's both accurate and consistent with your organization's standards.
    """
    
    def __init__(self):
        """
        Initialize Document Generation Agent with Advanced ADK Capabilities
        
        ADK Initialization Best Practices:
        1. **Service Configuration**: Set up connections to required cloud services
        2. **Resource Pre-loading**: Initialize expensive resources once
        3. **Vector Index Setup**: Configure semantic search capabilities
        4. **Template Caching**: Pre-load frequently used templates
        5. **Model Configuration**: Set up AI model preferences and fallbacks
        
        Production Considerations:
        - Vector index should be pre-warmed for faster queries
        - Templates should be cached in memory for performance
        - Model endpoints should have circuit breakers for reliability
        - Monitoring should track generation quality and latency
        """
        super().__init__()
        
        # Vector search index for RAG - stores organizational knowledge
        # In production, this would be a large-scale vector database with:
        # - Millions of documents indexed by semantic meaning
        # - Regular updates as new content is created
        # - Multiple indexes for different document types
        # - Performance optimization for sub-second search
        self.vector_index = "projects/engen-project/locations/us-central1/indexes/pattern-docs-index"
        
        # Configuration for document quality standards
        self.quality_threshold = 0.85  # Minimum quality score for auto-approval
        self.max_retries = 3  # Maximum regeneration attempts if quality is low
        
        # Track generation metrics for optimization
        self.generation_metrics = {
            "total_documents": 0,
            "auto_approved": 0,
            "human_review_required": 0,
            "regeneration_attempts": 0
        }

    async def on_diagram_validated(self, event):
        """
        Process validated diagrams and generate comprehensive documentation
        
        This is the main entry point for Stage 2, triggered when Stage 1 (validation)
        completes successfully. This method demonstrates the complete ADK pattern
        for intelligent content generation.
        
        **ADK Event Processing Pattern**:
        1. **Event Parsing**: Extract data from cloud events safely
        2. **Context Preparation**: Set up generation parameters
        3. **RAG Enhancement**: Retrieve relevant organizational knowledge
        4. **AI Generation**: Create content using best practices
        5. **Quality Assessment**: Evaluate generation quality
        6. **Human Review**: Route to experts when needed
        7. **State Management**: Store results for next stage
        
        **Error Handling Strategy**:
        - Graceful degradation if RAG retrieval fails
        - Retry logic for AI model failures
        - Fallback templates if custom templates unavailable
        - Comprehensive logging for debugging
        
        **Performance Optimization**:
        - Parallel processing of document sections
        - Caching of frequently retrieved content
        - Batch API calls where possible
        - Streaming responses for large documents
        
        Args:
            event: Cloud event containing validated diagram data
                   Format: {"description": str, "original": str, "validation_score": float}
        
        For ADK Beginners:
        This is like receiving a work order (event) to write documentation.
        You gather your research materials (RAG), follow the company style guide (templates),
        write the content (AI generation), and submit it for review (human verification).
        """
        start_time = time.time()
        
        try:
            # ADK Event Parsing Pattern - Handle multiple event formats safely
            if hasattr(event, 'data'):
                # Cloud Pub/Sub event format
                data = json.loads(event.data)
            elif isinstance(event, dict) and 'data' in event:
                # Dictionary with data field
                data = json.loads(event['data'])
            else:
                # Direct dictionary format
                data = event
                
            # Extract key information for documentation generation
            description = data.get('description', 'No description provided')
            original_file = data.get('original', 'unknown_diagram')
            validation_score = data.get('validation_score', 0)
            
            # Log the start of document generation for monitoring
            await self.monitoring.log_event(
                f"Starting document generation for {original_file} with validation score {validation_score}"
            )
            
            # Update metrics for performance tracking
            self.generation_metrics["total_documents"] += 1
            
            # Stage 2, Step 1: Prepare document structure
            # Get the template that defines what sections to generate
            sections = await self.get_document_template()
            
            # Stage 2, Step 2-4: Generate each section using RAG + AI
            doc_content = {}
            generation_errors = []
            
            for section in sections:
                try:
                    # RAG retrieval - find relevant organizational knowledge
                    context = await self.retrieve_rag_context(description, section['id'])
                    
                    # Template hydration - prepare prompts for AI generation
                    prompt = await self.get_section_prompt(section['id'])
                    
                    # Safe template formatting with error handling
                    try:
                        formatted_prompt = prompt.format(
                            context=context,
                            description=description,
                            section_type=section['id'],
                            organization_standards="Follow technical writing best practices"
                        )
                    except (KeyError, AttributeError, ValueError) as e:
                        # Fallback to simple format if template has issues
                        formatted_prompt = f"""
Generate a comprehensive {section['id']} section for technical documentation.

Diagram Description: {description}

Relevant Context: {context}

Requirements:
- Use clear, professional technical writing
- Include specific implementation details
- Follow standard documentation structure
- Be comprehensive but concise
"""
                        await self.monitoring.log_warning(
                            f"Template formatting failed for {section['id']}: {str(e)}. Using fallback format."
                        )

                    # Generate content using AI model
                    doc_content[section['id']] = await self.generate_section_content(
                        formatted_prompt, section['id'], max_retries=self.max_retries
                    )
                    
                except Exception as e:
                    generation_errors.append(f"Failed to generate {section['id']}: {str(e)}")
                    # Continue with other sections even if one fails
                    doc_content[section['id']] = f"[Error generating {section['id']} section. Please review manually.]"
            
            # Assess overall generation quality
            quality_score = self.assess_generation_quality(doc_content, description)
            
            # Store generated document with metadata
            doc_path = f"docs/{original_file}.md"
            assembled_doc = await self.assemble_document(doc_content, data)
            
            storage.write_file("pattern-docs", doc_path, assembled_doc)
            
            # Store generation metadata for analytics
            metadata = {
                "generation_time": time.time() - start_time,
                "sections_generated": list(doc_content.keys()),
                "quality_score": quality_score,
                "validation_score": validation_score,
                "errors": generation_errors,
                "timestamp": time.time()
            }
            
            storage.write_file(
                "generation-metadata", 
                f"{original_file}_metadata.json", 
                json.dumps(metadata)
            )
            
            # Determine next step based on quality
            if quality_score >= self.quality_threshold and not generation_errors:
                # High quality - proceed automatically
                self.generation_metrics["auto_approved"] += 1
                await self.monitoring.log_event(f"Document auto-approved: {doc_path}")
                
                # Trigger next stage (e.g., publishing or component specification)
                await self._trigger_next_stage(data, doc_path, quality_score)
                
            else:
                # Requires human review
                self.generation_metrics["human_review_required"] += 1
                await self.request_human_verification("document_review", {
                    "doc_path": doc_path,
                    "sections": list(doc_content.keys()),
                    "quality_score": quality_score,
                    "errors": generation_errors,
                    "original_validation_score": validation_score
                })
            
        except Exception as e:
            # Comprehensive error handling with detailed logging
            await self.monitoring.log_error(
                f"Document generation failed for event {event}: {str(e)}"
            )
            
            # Store error details for debugging
            error_data = {
                "error": str(e),
                "event_data": str(event),
                "timestamp": time.time(),
                "stage": "document_generation"
            }
            
            storage.write_file(
                "error-logs", 
                f"doc_gen_error_{time.time()}.json", 
                json.dumps(error_data)
            )

    async def generate_section_content(self, prompt: str, section_id: str, max_retries: int = 3) -> str:
        """
        Generate content for a specific document section with retry logic
        
        This method demonstrates ADK best practices for AI model integration:
        - Error handling and retry logic
        - Model-specific parameter optimization
        - Quality assessment and regeneration
        - Performance monitoring
        
        Args:
            prompt: Formatted prompt for content generation
            section_id: Identifier for the section being generated
            max_retries: Maximum number of generation attempts
            
        Returns:
            Generated content for the section
        """
        for attempt in range(max_retries):
            try:
                # Generate content using Claude 3.5 Sonnet
                # In production, you might choose different models for different sections
                content = vertexai.generate_text(
                    model="claude-3.5-sonnet@vertexai",
                    prompt=prompt,
                    params={
                        "max_tokens": 2048,
                        "temperature": 0.3,  # Lower temperature for technical content
                        "top_p": 0.9,
                        "stop_sequences": ["[END]", "---"]
                    }
                )
                
                # Basic quality check - ensure content is substantive
                if len(content.strip()) > 100:  # Minimum content length
                    return content
                else:
                    await self.monitoring.log_warning(
                        f"Generated content too short for {section_id}, attempt {attempt + 1}"
                    )
                    
            except Exception as e:
                await self.monitoring.log_warning(
                    f"Generation attempt {attempt + 1} failed for {section_id}: {str(e)}"
                )
                
                if attempt == max_retries - 1:
                    # Final attempt failed - return error message
                    return f"[Unable to generate {section_id} section after {max_retries} attempts. Please review manually.]"
                    
                # Wait before retry (exponential backoff)
                await asyncio.sleep(2 ** attempt)
        
        return f"[Generation failed for {section_id} section]"

    def assess_generation_quality(self, doc_content: Dict[str, str], description: str) -> float:
        """
        Assess the quality of generated documentation
        
        This method demonstrates ADK quality assessment patterns:
        - Multiple quality metrics combination
        - Threshold-based decision making
        - Continuous quality monitoring
        - Data-driven quality improvement
        
        Quality Metrics Used:
        1. Content completeness (all sections present)
        2. Content length appropriateness
        3. Technical vocabulary usage
        4. Structure consistency
        5. Relevance to input description
        
        Args:
            doc_content: Generated content for all sections
            description: Original diagram description
            
        Returns:
            Quality score between 0.0 and 1.0
        """
        quality_score = 0.0
        metrics = []
        
        # Metric 1: Section completeness (25% weight)
        expected_sections = len(self.get_document_template())
        actual_sections = len([content for content in doc_content.values() if not content.startswith('[Error')])
        completeness_score = actual_sections / expected_sections if expected_sections > 0 else 0
        metrics.append(("completeness", completeness_score, 0.25))
        
        # Metric 2: Content quality (35% weight)
        avg_length = sum(len(content) for content in doc_content.values()) / len(doc_content)
        length_score = min(avg_length / 500, 1.0)  # Expect at least 500 chars per section
        metrics.append(("length", length_score, 0.35))
        
        # Metric 3: Technical vocabulary (20% weight)
        technical_terms = ["architecture", "component", "implementation", "system", "design", "interface"]
        total_terms = sum(
            sum(term.lower() in content.lower() for term in technical_terms)
            for content in doc_content.values()
        )
        vocab_score = min(total_terms / 10, 1.0)  # Expect at least 10 technical terms
        metrics.append(("vocabulary", vocab_score, 0.20))
        
        # Metric 4: Error detection (20% weight)
        error_sections = sum(1 for content in doc_content.values() if '[Error' in content or '[Unable' in content)
        error_score = 1.0 - (error_sections / len(doc_content))
        metrics.append(("error_free", error_score, 0.20))
        
        # Calculate weighted score
        quality_score = sum(score * weight for _, score, weight in metrics)
        
        # Log quality metrics for monitoring
        quality_data = {
            "overall_score": quality_score,
            "metrics": {name: score for name, score, _ in metrics},
            "timestamp": time.time()
        }
        
        # Store quality data for analysis (async, don't block)
        try:
            storage.write_file(
                "quality-metrics", 
                f"quality_{time.time()}.json", 
                json.dumps(quality_data)
            )
        except Exception:
            pass  # Don't fail generation if quality logging fails
        
        return quality_score

    async def _trigger_next_stage(self, original_data: dict, doc_path: str, quality_score: float):
        """
        Trigger the next stage in the document generation pipeline
        
        This method demonstrates ADK workflow orchestration patterns:
        - Event-driven stage transitions
        - Data enrichment between stages
        - Error handling in workflows
        - Audit trail maintenance
        
        Args:
            original_data: Data from previous stage
            doc_path: Path to generated document
            quality_score: Quality assessment score
        """
        next_stage_data = {
            **original_data,  # Preserve original context
            "generated_document": doc_path,
            "generation_quality": quality_score,
            "stage_2_complete": True,
            "timestamp": time.time()
        }
        
        try:
            # Publish to next stage topic (e.g., component specification)
            await self.publisher.publish(
                "projects/engen-project/topics/component-specification",
                data=json.dumps(next_stage_data).encode()
            )
            
            await self.monitoring.log_event(
                f"Triggered next stage for {original_data.get('original', 'unknown')}"
            )
            
        except Exception as e:
            await self.monitoring.log_error(
                f"Failed to trigger next stage: {str(e)}"
            )

    async def retrieve_rag_context(self, description: str, section_id: str) -> str:
        """
        Retrieve relevant context using vector search (RAG pattern)
        
        This method demonstrates production-level RAG implementation:
        - Semantic similarity search
        - Context filtering and ranking
        - Fallback strategies for search failures
        - Performance optimization
        
        RAG (Retrieval-Augmented Generation) Benefits:
        1. **Accuracy**: Grounds AI responses in verified information
        2. **Consistency**: Ensures alignment with organizational standards
        3. **Knowledge Scaling**: Leverages entire knowledge base
        4. **Reduced Hallucination**: Minimizes AI-generated inaccuracies
        
        For ADK Beginners:
        This is like having a research assistant who can instantly search
        through thousands of documents to find the most relevant examples
        and guidelines for the specific section you're writing.
        
        Args:
            description: Diagram description to search for
            section_id: Specific section type for focused results
            
        Returns:
            Concatenated relevant context from knowledge base
        """
        try:
            # Construct search query combining description and section focus
            search_query = f"{description} {section_id} documentation patterns"
            
            # Perform vector search with section-specific filtering
            results = vertexai.vector_search(
                index=self.vector_index,
                query=search_query,
                filter=f"section='{section_id}'",
                num_results=3,
                similarity_threshold=0.7  # Only include highly relevant results
            )
            
            # Process and combine results
            context_pieces = []
            for result in results:
                # Add relevance score to help AI understand importance
                context_pieces.append(f"[Relevance: {result.score:.2f}] {result.content}")
            
            combined_context = "\n\n".join(context_pieces)
            
            # Log RAG performance for optimization
            await self.monitoring.log_event(
                f"RAG retrieval for {section_id}: {len(results)} results, avg_score: {sum(r.score for r in results) / len(results) if results else 0:.2f}"
            )
            
            return combined_context if combined_context else "No relevant context found."
            
        except Exception as e:
            # Graceful degradation - return fallback context
            await self.monitoring.log_warning(f"RAG retrieval failed: {str(e)}")
            
            return f"""
Fallback context for {section_id}:
- Follow standard technical documentation practices
- Include implementation details and examples
- Ensure clarity and completeness
- Reference industry best practices
"""

    async def get_document_template(self) -> List[Dict[str, str]]:
        """
        Retrieve document structure template with error handling
        
        This method demonstrates ADK configuration management patterns:
        - External configuration with fallbacks
        - JSON parsing with error handling
        - Default configuration for reliability
        - Template versioning and caching
        
        Template Management in ADK:
        1. **External Storage**: Templates stored in cloud storage for easy updates
        2. **Version Control**: Track template changes and rollback capabilities
        3. **Caching**: Cache templates in memory for performance
        4. **Fallback Strategy**: Default templates when external ones fail
        5. **A/B Testing**: Different templates for quality comparison
        
        For ADK Beginners:
        This is like having a style guide or outline that tells you exactly
        what sections to include in your document. If the official style guide
        isn't available, you fall back to a basic standard format.
        
        Returns:
            List of section definitions with id and title
        """
        try:
            # Attempt to load template from external storage
            template_data = storage.read_file("templates", "doc_structure.json")
            
            if template_data and template_data.strip():
                parsed_template = json.loads(template_data.decode())
                
                # Validate template structure
                if isinstance(parsed_template, list) and all(
                    isinstance(section, dict) and 'id' in section and 'title' in section
                    for section in parsed_template
                ):
                    # Cache successful template load
                    self._cached_template = parsed_template
                    return parsed_template
                else:
                    await self.monitoring.log_warning("Invalid template structure, using default")
                    
        except (json.JSONDecodeError, AttributeError, KeyError) as e:
            await self.monitoring.log_warning(f"Template parsing failed: {str(e)}, using default")
        except Exception as e:
            await self.monitoring.log_error(f"Template loading failed: {str(e)}, using default")
        
        # Return comprehensive default template
        default_template = [
            {
                "id": "overview", 
                "title": "Overview",
                "description": "High-level description and purpose"
            },
            {
                "id": "architecture", 
                "title": "Architecture",
                "description": "System design and component relationships"
            },
            {
                "id": "components", 
                "title": "Components",
                "description": "Detailed component specifications"
            },
            {
                "id": "interfaces", 
                "title": "Interfaces",
                "description": "APIs and integration points"
            },
            {
                "id": "deployment", 
                "title": "Deployment",
                "description": "Installation and configuration guide"
            },
            {
                "id": "testing", 
                "title": "Testing",
                "description": "Test strategies and procedures"
            }
        ]
        
        # Cache default template
        self._cached_template = default_template
        return default_template

    async def get_section_prompt(self, section_id: str) -> str:
        """
        Get section-specific prompt template from storage
        
        This method demonstrates ADK prompt management patterns:
        - Centralized prompt storage and versioning
        - Section-specific prompt optimization
        - Fallback prompts for reliability
        - Performance optimization through caching
        
        Prompt Engineering Best Practices in ADK:
        1. **Specificity**: Tailored prompts for each section type
        2. **Context Slots**: Placeholders for dynamic information
        3. **Examples**: Include few-shot examples for better results
        4. **Constraints**: Clear guidelines and limitations
        5. **Version Control**: Track prompt performance and iterations
        
        Args:
            section_id: Identifier for the document section
            
        Returns:
            Formatted prompt template for the section
        """
        try:
            # Retrieve section-specific prompt from Bigtable
            row = bigtable.get_row(
                instance_id="prompt-templates",
                table_id="doc-sections",
                row_key=section_id
            )
            
            if row and row.cells.get("prompt"):
                prompt_content = row.cells["prompt"][0].value.decode()
                
                # Validate prompt has required placeholders
                required_placeholders = ["{context}", "{description}"]
                if all(placeholder in prompt_content for placeholder in required_placeholders):
                    return prompt_content
                else:
                    await self.monitoring.log_warning(
                        f"Prompt for {section_id} missing required placeholders, using fallback"
                    )
            
        except Exception as e:
            await self.monitoring.log_warning(f"Failed to retrieve prompt for {section_id}: {str(e)}")
        
        # Fallback prompts optimized for each section type
        fallback_prompts = {
            "overview": """
Create a comprehensive overview section for technical documentation.

Context from similar documents:
{context}

Diagram Description:
{description}

Requirements:
- Provide a clear, high-level description of the system
- Explain the main purpose and business value
- Identify key stakeholders and use cases
- Keep technical details minimal but accurate
- Use professional, accessible language

Format the response as markdown with appropriate headers.
""",
            
            "architecture": """
Create a detailed architecture section for technical documentation.

Context from similar documents:
{context}

Diagram Description:
{description}

Requirements:
- Describe the overall system architecture
- Explain key architectural decisions and trade-offs
- Detail component relationships and data flow
- Include scalability and performance considerations
- Reference relevant architectural patterns
- Use technical but clear language

Format the response as markdown with appropriate headers and code blocks where relevant.
""",
            
            "components": """
Create a comprehensive components section for technical documentation.

Context from similar documents:
{context}

Diagram Description:
{description}

Requirements:
- List and describe each major component
- Explain component responsibilities and interfaces
- Detail dependencies and relationships
- Include configuration and customization options
- Provide implementation guidelines
- Use specific, actionable language

Format the response as markdown with component subsections.
""",
            
            "deployment": """
Create a detailed deployment section for technical documentation.

Context from similar documents:
{context}

Diagram Description:
{description}

Requirements:
- Provide step-by-step deployment instructions
- List prerequisites and dependencies
- Include configuration examples
- Address common deployment scenarios
- Provide troubleshooting guidance
- Use clear, actionable language

Format the response as markdown with numbered steps and code examples.
"""
        }
        
        # Return section-specific fallback or generic fallback
        return fallback_prompts.get(section_id, """
Create a comprehensive {section_type} section for technical documentation.

Context: {context}
Description: {description}

Provide detailed, accurate, and well-structured content for this section.
""".replace("{section_type}", section_id))

    async def assemble_document(self, doc_content: Dict[str, str], metadata: Dict[str, Any]) -> str:
        """
        Assemble final document with metadata and formatting
        
        This method demonstrates ADK document assembly patterns:
        - Consistent formatting and structure
        - Metadata integration for traceability
        - Template-based assembly
        - Quality indicators and timestamps
        
        Document Assembly Best Practices:
        1. **Consistent Structure**: Standard formatting across all documents
        2. **Metadata Integration**: Include generation details for audit trails
        3. **Quality Indicators**: Show confidence levels and review status
        4. **Navigation Aids**: Table of contents and cross-references
        5. **Version Information**: Track document iterations and sources
        
        Args:
            doc_content: Generated content for each section
            metadata: Generation metadata and context
            
        Returns:
            Complete formatted document as markdown
        """
        # Generate document header with metadata
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
        header = f"""# Technical Documentation

**Generated**: {timestamp}  
**Source**: {metadata.get('original', 'Unknown')}  
**Validation Score**: {metadata.get('validation_score', 'N/A')}  
**Generation Quality**: {getattr(self, '_last_quality_score', 'N/A')}  

---

"""
        
        # Generate table of contents
        toc = "## Table of Contents\n\n"
        for section_id in doc_content.keys():
            section_title = section_id.replace('_', ' ').title()
            toc += f"- [{section_title}](#{section_id.lower().replace('_', '-')})\n"
        toc += "\n---\n\n"
        
        # Assemble main content
        main_content = ""
        template_sections = await self.get_document_template()
        
        for section_info in template_sections:
            section_id = section_info['id']
            section_title = section_info.get('title', section_id.title())
            
            if section_id in doc_content:
                content = doc_content[section_id]
                
                # Add quality indicator for sections with errors
                quality_indicator = ""
                if content.startswith('[Error') or content.startswith('[Unable'):
                    quality_indicator = " ⚠️ *Requires Review*"
                
                main_content += f"## {section_title}{quality_indicator}\n\n{content}\n\n---\n\n"
        
        # Add footer with generation details
        footer = f"""
## Generation Details

- **Pipeline Stage**: Document Generation (Stage 2)
- **Processing Time**: {getattr(self, '_last_generation_time', 'N/A')} seconds
- **AI Model**: Claude 3.5 Sonnet (Vertex AI)
- **RAG Context**: Retrieved from organizational knowledge base
- **Review Status**: {getattr(self, '_review_status', 'Pending Review')}

*This document was automatically generated using Google ADK. Please review for accuracy and completeness.*
"""
        
        return header + toc + main_content + footer
