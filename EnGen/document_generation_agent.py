"""
Document Generation Agent - Stage 2
Generates comprehensive documentation from validated diagrams
"""

import json
from typing import Dict, Any, List, Optional
from base_agent import Agent
from mock_services import storage, vertexai, pubsub, bigtable


class DocumentGenerationAgent(Agent):
    """Stage 2: Generates comprehensive documentation from validated diagrams"""
    
    def __init__(self):
        super().__init__()
        self.vector_index = "projects/engen-project/locations/us-central1/indexes/pattern-docs-index"

    async def on_diagram_validated(self, event):
        """Process validated diagrams"""
        # Handle both dict and object with data attribute
        if hasattr(event, 'data'):
            data = json.loads(event.data)
        elif isinstance(event, dict) and 'data' in event:
            data = json.loads(event['data'])
        else:
            data = event
            
        description = data['description']

        # Stage 2, Step 1: Prepare document sections
        sections = self.get_document_template()

        # Stage 2, Step 2-4: Generate each section
        doc_content = {}
        for section in sections:
            # RAG retrieval
            context = await self.retrieve_rag_context(description, section['id'])

            # Template hydration
            prompt = self.get_section_prompt(section['id'])
            try:
                formatted_prompt = prompt.format(
                    context=context,
                    description=description
                )
            except (KeyError, AttributeError):
                # If template has missing keys or is invalid, use simple format
                formatted_prompt = f"Generate {section['id']} section based on: {description}\nContext: {context}"

            # Generate content
            doc_content[section['id']] = vertexai.generate_text(
                model="claude-3.5-sonnet@vertexai",
                prompt=formatted_prompt,
                params={"max_tokens": 2048}
            )

        # Store document
        doc_path = f"docs/{data['original']}.md"
        storage.write_file("pattern-docs", doc_path, self.assemble_document(doc_content))

        # Human verification
        await self.request_human_verification("document", {
            "doc_path": doc_path,
            "sections": list(doc_content.keys())
        })

    async def retrieve_rag_context(self, description: str, section_id: str) -> str:
        """Vector search for relevant content"""
        results = vertexai.vector_search(
            index=self.vector_index,
            query=description,
            filter=f"section='{section_id}'",
            num_results=3
        )
        return "\n\n".join([r.content for r in results])

    def get_document_template(self) -> list:
        """Retrieve document structure"""
        try:
            template = storage.read_file("templates", "doc_structure.json").decode()
            if template and template.strip():
                return json.loads(template)
        except (json.JSONDecodeError, AttributeError):
            pass
        
        # Return default template if parsing fails
        return [
            {"id": "overview", "title": "Overview"},
            {"id": "architecture", "title": "Architecture"},
            {"id": "components", "title": "Components"},
            {"id": "deployment", "title": "Deployment"}
        ]

    def get_section_prompt(self, section_id: str) -> str:
        """Get section-specific prompt"""
        row = bigtable.get_row(
            instance_id="prompt-templates",
            table_id="doc-sections",
            row_key=section_id
        )
        return row.cells["prompt"][0].value.decode()

    def assemble_document(self, doc_content: dict) -> str:
        """Assemble final document"""
        document = "# Pattern Documentation\n\n"
        for section_id, content in doc_content.items():
            document += f"## {section_id.title()}\n\n{content}\n\n"
        return document
