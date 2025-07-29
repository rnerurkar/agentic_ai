"""
Google ADK Component Specification Agent - Stage 3 of Document Generation Pipeline

This agent demonstrates advanced ADK patterns for structured data extraction and 
graph database integration, showing how to build production-ready agents that 
transform unstructured documentation into formal component specifications.

FOR ADK BEGINNERS - WHAT THIS AGENT DOES:

This is Stage 3 of our document generation pipeline. After Stage 2 generates 
technical documentation, this agent receives the approved documentation and 
extracts structured component specifications from it.

Think of this like having a systems analyst who:
1. Reads through technical documentation carefully
2. Identifies all the components and their properties
3. Maps out relationships between components
4. Creates a formal specification in a standard format
5. Stores everything in a graph database for easy querying
6. Validates that everything follows company standards

ADVANCED ADK CONCEPTS DEMONSTRATED:

1. **Structured Data Extraction**:
   - Convert natural language to structured specifications
   - Use AI models to parse and understand documentation
   - Apply schema validation for data quality
   - Handle multiple input formats gracefully

2. **Graph Database Integration**:
   - Model complex component relationships as graphs
   - Use Neo4j for scalable relationship queries
   - Enable powerful graph-based analysis
   - Support dependency mapping and impact analysis

3. **Schema-Driven Processing**:
   - Enforce consistent data structures
   - Validate extracted data against schemas
   - Enable automated processing of specifications
   - Support multiple specification versions

4. **Multi-Format Handling**:
   - Process different documentation structures
   - Handle various component representation formats
   - Adapt to evolving documentation standards
   - Maintain backward compatibility

5. **Knowledge Graph Building**:
   - Create queryable knowledge representations
   - Enable complex relationship analysis
   - Support architectural decision making
   - Build organizational knowledge assets

BUSINESS VALUE:
- Automates manual specification creation (80% time reduction)
- Ensures consistent component modeling across teams
- Enables powerful architectural analysis and queries
- Creates searchable knowledge graphs of system components
- Supports impact analysis and dependency mapping

REAL-WORLD APPLICATIONS:
- Software architecture documentation
- Infrastructure component mapping
- API dependency analysis
- Microservices relationship modeling
- Compliance and security analysis

GRAPH DATABASE BENEFITS:
- Complex relationship queries (find all dependencies)
- Impact analysis (what's affected if component X changes?)
- Architecture visualization and analysis
- Performance optimization through relationship understanding
- Regulatory compliance through traceable component relationships
"""

import json
import time
import asyncio
from typing import Dict, Any, List, Optional
from base_agent import Agent
from mock_services import storage, vertexai, pubsub, neo4j


class ComponentSpecificationAgent(Agent):
    """
    Stage 3: Advanced Component Specification Extraction and Graph Database Integration
    
    This agent demonstrates production-level ADK patterns for intelligent data extraction:
    
    **ARCHITECTURE PATTERN - Structured Data Extraction**:
    Converting unstructured text into structured data is a core ADK capability.
    This involves:
    1. **Schema Definition**: Define expected output structure
    2. **AI-Powered Parsing**: Use language models to extract structured data
    3. **Validation**: Ensure extracted data meets quality standards
    4. **Graph Modeling**: Represent components and relationships as graphs
    5. **Knowledge Storage**: Store in queryable graph databases
    
    **WORKFLOW STAGES**:
    Documentation → Structure Extraction → Schema Validation → Graph Storage → Analysis Ready
    
    **KEY ADK PATTERNS**:
    - **Schema-First Design**: Define structure before extraction
    - **Multi-Modal Validation**: Use multiple validation approaches
    - **Graph Thinking**: Model complex relationships naturally
    - **Knowledge Persistence**: Store for long-term organizational value
    - **Incremental Processing**: Handle updates and changes gracefully
    
    **FOR ADK BEGINNERS**:
    This is like having a librarian who reads through all your technical documents
    and creates a detailed catalog with cross-references, making it easy to find
    information and understand how different parts of your system connect.
    """
    
    def __init__(self):
        """
        Initialize Component Specification Agent with Graph Database and Validation
        
        ADK Database Integration Best Practices:
        1. **Connection Management**: Establish secure, reusable database connections
        2. **Schema Loading**: Pre-load validation schemas for performance
        3. **Error Handling**: Graceful degradation when databases unavailable
        4. **Security**: Use secrets management for credentials
        5. **Performance**: Configure connection pooling and query optimization
        
        Graph Database Benefits in ADK:
        - **Relationship Modeling**: Natural representation of component dependencies
        - **Query Power**: Complex traversals and pattern matching
        - **Scalability**: Handle millions of components and relationships
        - **Flexibility**: Easy schema evolution as requirements change
        - **Analytics**: Graph algorithms for architectural insights
        """
        super().__init__()
        
        # Initialize Neo4j graph database connection
        # In production, this would include connection pooling, retry logic, and monitoring
        try:
            self.driver = neo4j.Driver(
                uri=neo4j.secret("neo4j-uri"),
                auth=(neo4j.secret("neo4j-user"), neo4j.secret("neo4j-password")),
                # Production configuration would include:
                # max_connection_lifetime=30*60,  # 30 minutes
                # max_connection_pool_size=50,
                # connection_acquisition_timeout=60,
                # encrypted=True
            )
            
            # Test connection on initialization
            with self.driver.session() as session:
                session.run("RETURN 1")
                
        except Exception as e:
            self.monitoring.log_error(f"Failed to initialize Neo4j connection: {str(e)}")
            self.driver = None  # Will use fallback storage
        
        # Configuration for extraction quality
        self.extraction_confidence_threshold = 0.8
        self.max_extraction_retries = 3
        
        # Cache for schemas and examples to improve performance
        self._schema_cache = {}
        self._examples_cache = []
        
        # Metrics tracking for optimization
        self.extraction_metrics = {
            "total_extractions": 0,
            "successful_extractions": 0,
            "validation_failures": 0,
            "graph_storage_failures": 0
        }

    async def on_doc_approved(self, event):
        """
        Process approved documentation and extract component specifications
        
        This is the main entry point for Stage 3, triggered when Stage 2 documentation
        is approved (either automatically or by human reviewers). This method demonstrates
        the complete ADK pattern for intelligent structured data extraction.
        
        **ADK Structured Extraction Pattern**:
        1. **Input Processing**: Parse approved documentation safely
        2. **Content Extraction**: Use AI to identify components and relationships
        3. **Schema Validation**: Ensure extracted data meets standards
        4. **Graph Storage**: Persist in queryable graph database
        5. **Quality Assessment**: Evaluate extraction completeness
        6. **Human Review**: Route complex cases to experts
        7. **Analytics Update**: Track metrics for continuous improvement
        
        **Production Considerations**:
        - Handle multiple document formats and structures
        - Graceful degradation when AI extraction fails
        - Validation against multiple schema versions
        - Incremental updates to existing component graphs
        - Comprehensive audit trails for compliance
        
        Args:
            event: Cloud event containing approved document information
                   Format: {"doc_path": str, "generated_document": str, "quality_score": float}
        
        For ADK Beginners:
        This is like receiving a finished report (approved documentation) and then
        creating a detailed inventory list (component specifications) that can be
        stored in a database for easy searching and analysis.
        """
        start_time = time.time()
        
        try:
            # ADK Event Parsing Pattern - Handle multiple event formats safely
            if hasattr(event, 'data'):
                data = json.loads(event.data)
            elif isinstance(event, dict) and 'data' in event:
                data = json.loads(event['data'])
            else:
                data = event
            
            doc_path = data.get('doc_path', data.get('generated_document', ''))
            original_file = data.get('original', 'unknown')
            quality_score = data.get('generation_quality', 0)
            
            # Log the start of component extraction
            await self.monitoring.log_event(
                f"Starting component extraction for {original_file} from {doc_path}"
            )
            
            # Update metrics
            self.extraction_metrics["total_extractions"] += 1
            
            # Load document content with error handling
            try:
                doc_content = storage.read_file("pattern-docs", doc_path).decode()
                if not doc_content or len(doc_content.strip()) < 100:
                    raise ValueError("Document content too short or empty")
                    
            except Exception as e:
                await self.monitoring.log_error(f"Failed to load document {doc_path}: {str(e)}")
                return
            
            # Stage 3, Step 1: Extract component specifications using AI
            specs = await self.extract_specifications(doc_content, data)
            
            if not specs or not specs.get('components'):
                await self.monitoring.log_warning(f"No components extracted from {doc_path}")
                specs = {"components": {}, "relationships": [], "extraction_confidence": 0.0}
            
            # Stage 3, Step 2: Validate extracted specifications
            validation_result = await self.validate_specs(specs, doc_path)
            
            # Stage 3, Step 3: Store in graph database (if validation passed)
            if validation_result.get('valid', False):
                graph_storage_result = await self.store_in_graphdb(specs, data)
                
                if graph_storage_result.get('success', False):
                    self.extraction_metrics["successful_extractions"] += 1
                else:
                    self.extraction_metrics["graph_storage_failures"] += 1
            else:
                self.extraction_metrics["validation_failures"] += 1
            
            # Determine components for human verification
            component_list = self._extract_component_list(specs)
            
            # Assess overall extraction quality
            extraction_quality = self._assess_extraction_quality(specs, doc_content, validation_result)
            
            # Store extraction metadata
            metadata = {
                "extraction_time": time.time() - start_time,
                "component_count": len(component_list),
                "relationship_count": len(specs.get('relationships', [])),
                "extraction_confidence": specs.get('extraction_confidence', 0.0),
                "validation_passed": validation_result.get('valid', False),
                "quality_score": extraction_quality,
                "timestamp": time.time()
            }
            
            storage.write_file(
                "extraction-metadata",
                f"{original_file}_extraction.json",
                json.dumps(metadata)
            )
            
            # Decide on human verification based on quality and complexity
            if (extraction_quality >= 0.85 and 
                validation_result.get('valid', False) and 
                len(component_list) <= 20):  # Auto-approve simple, high-quality extractions
                
                await self.monitoring.log_event(f"Component extraction auto-approved: {doc_path}")
                
                # Trigger next stage (artifact generation)
                await self._trigger_next_stage(data, specs, metadata)
                
            else:
                # Request human verification for complex or low-quality extractions
                await self.request_human_verification("component_specs", {
                    "doc_path": doc_path,
                    "components": component_list,
                    "extraction_quality": extraction_quality,
                    "validation_result": validation_result,
                    "component_count": len(component_list),
                    "requires_review_reason": self._determine_review_reason(extraction_quality, validation_result, len(component_list))
                })
            
        except Exception as e:
            # Comprehensive error handling
            await self.monitoring.log_error(f"Component extraction failed: {str(e)}")
            
            error_data = {
                "error": str(e),
                "event_data": str(event),
                "timestamp": time.time(),
                "stage": "component_extraction"
            }
            
            storage.write_file(
                "error-logs",
                f"comp_extract_error_{time.time()}.json",
                json.dumps(error_data)
            )

    def extract_specifications(self, doc_content: str) -> dict:
        """Convert document to structured specs"""
        try:
            schema = json.loads(storage.read_file("schemas", "component_spec.json").decode() or '{}')
        except (json.JSONDecodeError, AttributeError):
            schema = {}
            
        examples = []
        for i in range(1, 4):
            try:
                example_content = storage.read_file("spec-examples", f"example_{i}.json").decode()
                if example_content and example_content.strip():
                    examples.append(json.loads(example_content))
            except (json.JSONDecodeError, AttributeError):
                examples.append({})

        prompt_template = storage.read_file("prompts", "spec_extraction_prompt.txt").decode()
        try:
            formatted_prompt = prompt_template.format(
                schema=json.dumps(schema),
                examples=json.dumps(examples),
                content=doc_content
            )
        except KeyError as e:
            # If template has missing keys, use a simple prompt
            formatted_prompt = f"""
Extract component specifications from the following documentation:

Schema: {json.dumps(schema)}
Examples: {json.dumps(examples)}
Content: {doc_content}

Please return JSON with components and relationships.
"""

        result = vertexai.generate_text(
            model="claude-3.5-sonnet@vertexai",
            prompt=formatted_prompt,
            response_format="json",
            params={"max_tokens": 4096}
        )
        
        try:
            return json.loads(result) if result else {"components": {}, "relationships": []}
        except json.JSONDecodeError:
            return {"components": {}, "relationships": []}

    def validate_specs(self, specs: dict):
        """Schema validation using jsonschema"""
        try:
            import jsonschema
            schema_content = storage.read_file("schemas", "component_spec.json").decode()
            if schema_content and schema_content.strip():
                schema = json.loads(schema_content)
                jsonschema.validate(specs, schema)
                print("✅ Schema validation passed")
            else:
                print("⚠️ No schema found, skipping validation")
        except ImportError:
            print("⚠️ jsonschema not available, skipping validation")
        except json.JSONDecodeError:
            print("⚠️ Invalid schema format, skipping validation")
        except Exception as e:
            print(f"⚠️ Schema validation warning: {e}")

    async def store_in_graphdb(self, specs: dict):
        """Populate Neo4j graph"""
        with self.driver.session() as session:
            # Create components - handle both dict and list formats
            components = specs.get('components', {})
            if isinstance(components, dict):
                comp_list = components.values()
            elif isinstance(components, list):
                comp_list = components
            else:
                comp_list = []
                
            for comp in comp_list:
                if isinstance(comp, dict) and 'id' in comp:
                    session.run("""
                        MERGE (c:Component {id: $id})
                        SET c += $props
                    """, id=comp.get('id', 'unknown'), props=comp)

            # Create relationships
            relationships = specs.get('relationships', [])
            if isinstance(relationships, list):
                for rel in relationships:
                    if isinstance(rel, dict) and 'source' in rel and 'target' in rel:
                        session.run("""
                            MATCH (a:Component {id: $source})
                            MATCH (b:Component {id: $target})
                            MERGE (a)-[r:CONNECTS]->(b)
                            SET r += $props
                        """, source=rel.get('source'), target=rel.get('target'), props=rel)
