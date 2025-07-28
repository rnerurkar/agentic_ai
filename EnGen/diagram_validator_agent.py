"""
Diagram Validator Agent - Stage 1
Validates uploaded diagrams using Gemini Vision
"""

import json
from typing import Dict, Any, List, Optional
from base_agent import Agent
from mock_services import storage, vertexai, pubsub


class DiagramValidatorAgent(Agent):
    """Stage 1: Validates uploaded diagrams using Gemini Vision"""
    
    def __init__(self):
        super().__init__()
        self.publisher = pubsub
        self.topic_path = "projects/engen-project/topics/validated-diagrams"

    async def on_gcs_upload(self, event):
        """Triggered by new diagram upload"""
        try:
            # Stage 1, Step 1: Process upload
            bucket = event['bucket']
            file_path = event['name']
            diagram = storage.read_file(bucket, file_path)

            # Stage 1, Step 2: Validate diagram
            validation_result = await self.validate_diagram(diagram)

            if validation_result['score'] >= 80:  # Approval threshold
                # Stage 1, Step 3: Generate description
                description = await self.generate_description(diagram, validation_result)

                # Store for next stage
                output_path = f"validated/{file_path}.json"
                storage.write_file("engen-diagrams", output_path, json.dumps({
                    "original": file_path,
                    "validation": validation_result,
                    "description": description
                }))

                # Human verification checkpoint
                await self.request_human_verification("diagram", {
                    "diagram": file_path,
                    "validation": validation_result,
                    "description": description
                })
            else:
                await self.handle_rejection(validation_result)

        except Exception as e:
            await self.monitoring.log_error(f"Validation failed: {str(e)}")

    async def validate_diagram(self, diagram: bytes) -> dict:
        """Gemini Vision validation against reference patterns"""
        reference_diagrams = [
            storage.read_file("reference-patterns", f"pattern_{i}.png")
            for i in range(1, 66)
        ]

        return vertexai.analyze_image(
            model="gemini-1.5-pro-vision",
            image=diagram,
            prompt=storage.read_file("prompts", "diagram_validation_prompt.txt").decode(),
            reference_images=reference_diagrams,
            params={"temperature": 0.0, "max_output_tokens": 1024}
        )

    async def generate_description(self, diagram: bytes, validation: dict) -> str:
        """Generate pattern description using Claude 3.5"""
        prompt_template = storage.read_file("prompts", "description_prompt.txt").decode()
        formatted_prompt = prompt_template.format(validation=json.dumps(validation))
        
        return vertexai.generate_text(
            model="claude-3.5-sonnet@vertexai",
            prompt=formatted_prompt,
            image=diagram,
            params={"max_tokens": 4096}
        )

    async def handle_rejection(self, validation_result: dict):
        """Handle rejected diagrams"""
        print(f"Diagram rejected: score {validation_result['score']} below threshold")

    async def on_human_approval(self, event):
        """Handle human verification result"""
        if event['approved']:
            await self.publisher.publish(
                self.topic_path,
                data=json.dumps(event['context']).encode()
            )
