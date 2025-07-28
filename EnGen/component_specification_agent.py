"""
Component Specification Agent - Stage 3
Extracts and validates component specifications
"""

import json
from typing import Dict, Any, List, Optional
from base_agent import Agent
from mock_services import storage, vertexai, pubsub, neo4j


class ComponentSpecificationAgent(Agent):
    """Stage 3: Extracts and validates component specifications"""
    
    def __init__(self):
        super().__init__()
        self.driver = neo4j.Driver(
            uri=neo4j.secret("neo4j-uri"),
            auth=(neo4j.secret("neo4j-user"), neo4j.secret("neo4j-password"))
        )

    async def on_doc_approved(self, event):
        """Process approved documents"""
        # Handle both dict and object with data attribute
        if hasattr(event, 'data'):
            data = json.loads(event.data)
        elif isinstance(event, dict) and 'data' in event:
            data = json.loads(event['data'])
        else:
            data = event
            
        doc_content = storage.read_file("pattern-docs", data['doc_path']).decode()

        # Stage 3, Step 1: Extract specs
        specs = self.extract_specifications(doc_content)

        # Stage 3, Step 2: Validate schema
        self.validate_specs(specs)

        # Stage 3, Step 3: Store in Neo4j
        await self.store_in_graphdb(specs)

        # Human verification
        component_list = []
        if 'components' in specs:
            components = specs['components']
            if isinstance(components, dict):
                component_list = list(components.keys())
            elif isinstance(components, list):
                component_list = [comp.get('id', f'comp_{i}') for i, comp in enumerate(components) if isinstance(comp, dict)]
            
        await self.request_human_verification("specs", {
            "doc_path": data['doc_path'],
            "components": component_list
        })

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
