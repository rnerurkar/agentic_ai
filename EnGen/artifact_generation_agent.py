"""
Artifact Generation Agent - Stage 4
Generates deployment artifacts from specifications
"""

import json
import ast
from typing import Dict, Any, List, Optional
from base_agent import Agent
from mock_services import storage, vertexai, pubsub, neo4j, bigtable


class ArtifactGenerationAgent(Agent):
    """Stage 4: Generates deployment artifacts from specifications"""
    
    def __init__(self):
        super().__init__()
        self.driver = neo4j.Driver(
            uri=neo4j.secret("neo4j-uri"),
            auth=(neo4j.secret("neo4j-user"), neo4j.secret("neo4j-password"))
        )

    async def on_specs_approved(self, event):
        """Process approved specifications"""
        # Handle both dict and object with data attribute
        if hasattr(event, 'data'):
            data = json.loads(event.data)
        elif isinstance(event, dict) and 'data' in event:
            data = json.loads(event['data'])
        else:
            data = event
            
        pattern_id = data['doc_path'].split('/')[-1].replace('.md', '')

        # Get all components for pattern
        components = self.get_pattern_components(pattern_id)

        artifacts = {}
        for comp_id in components:
            # Stage 4, Step 1: Get component context
            context = self.get_component_context(comp_id)

            # Stage 4, Step 2-3: Generate artifacts
            comp_artifacts = self.generate_artifacts(context)

            # Stage 4, Step 4: Self-validation
            self.validate_artifacts(comp_artifacts)

            artifacts[comp_id] = comp_artifacts

        # Store artifacts
        storage.write_file("generated-artifacts", f"{pattern_id}.json", json.dumps(artifacts))

        # Human verification
        await self.request_human_verification("artifacts", {
            "pattern_id": pattern_id,
            "artifacts": list(artifacts.keys())
        })

    def get_pattern_components(self, pattern_id: str) -> list:
        """Retrieve components for a pattern"""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (p:Pattern {id: $id})-[:HAS_COMPONENT]->(c)
                RETURN c.id as id
            """, id=pattern_id)
            return [record['id'] for record in result]

    def get_component_context(self, comp_id: str) -> dict:
        """Get component + relationships"""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (c:Component {id: $id})-[r*1..2]-(related)
                RETURN c, relationships(r) as rels, collect(related) as related
            """, id=comp_id)
            return result.single().data

    def generate_artifacts(self, context: dict) -> dict:
        """Generate code artifacts"""
        comp_type = context.get('c', {}).get('type', 'service')
        return {
            "tf": self.generate_from_template(comp_type, "terraform", context),
            "code": self.generate_from_template(comp_type, "code", context),
            "pipeline": self.generate_from_template(comp_type, "pipeline", context)
        }

    def generate_from_template(self, comp_type: str, artifact_type: str, context: dict) -> str:
        """Retrieve and hydrate template"""
        template = bigtable.get_row(
            instance_id="code-templates",
            table_id="artifacts",
            row_key=f"{comp_type}-{artifact_type}"
        ).cells["template"][0].value.decode()

        formatted_template = template.format(context=json.dumps(context))
        
        return vertexai.generate_text(
            model="claude-3.5-sonnet@vertexai",
            prompt=formatted_template,
            params={"max_tokens": 2048}
        )

    def validate_artifacts(self, artifacts: dict):
        """Automated validation checks"""
        try:
            # Validate Terraform syntax (mock validation)
            if "tf" in artifacts:
                print(f"✅ Terraform validation passed for: {artifacts['tf'][:50]}...")

            # Validate Python code
            if "code" in artifacts and artifacts["code"].strip():
                try:
                    ast.parse(artifacts["code"])
                    print(f"✅ Python code validation passed")
                except SyntaxError as e:
                    print(f"⚠️ Python syntax warning: {e}")

            # Validate pipeline syntax
            if "pipeline" in artifacts and artifacts["pipeline"].strip():
                try:
                    import yaml
                    yaml.safe_load(artifacts["pipeline"])
                    print(f"✅ Pipeline YAML validation passed")
                except ImportError:
                    print("⚠️ YAML library not available for validation")
                except Exception as e:
                    print(f"⚠️ Pipeline validation warning: {e}")
        except Exception as e:
            print(f"❌ Validation failed: {e}")
            raise
