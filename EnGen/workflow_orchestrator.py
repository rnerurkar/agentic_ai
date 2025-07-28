"""
EnGen Workflow Orchestrator
Test program that demonstrates the complete agentic AI workflow
"""

import asyncio
import json
from typing import Dict, Any

# Import all agents
from diagram_validator_agent import DiagramValidatorAgent
from document_generation_agent import DocumentGenerationAgent
from component_specification_agent import ComponentSpecificationAgent
from artifact_generation_agent import ArtifactGenerationAgent
from human_verifier_agent import HumanVerifierAgent


class WorkflowOrchestrator:
    """Orchestrates the complete EnGen workflow"""
    
    def __init__(self):
        # Initialize all agents
        self.diagram_agent = DiagramValidatorAgent()
        self.doc_agent = DocumentGenerationAgent()
        self.spec_agent = ComponentSpecificationAgent()
        self.artifact_agent = ArtifactGenerationAgent()
        self.human_agent = HumanVerifierAgent()
        
        # Workflow state
        self.workflow_state = {}
        self.current_stage = 1
        
    async def start_workflow(self, diagram_upload_event: Dict[str, Any]):
        """Start the complete workflow with a diagram upload"""
        print("🚀 Starting EnGen Workflow")
        print("=" * 50)
        
        try:
            # Stage 1: Diagram Validation
            await self.run_stage_1(diagram_upload_event)
            
            # Stage 2: Document Generation
            await self.run_stage_2()
            
            # Stage 3: Component Specification
            await self.run_stage_3()
            
            # Stage 4: Artifact Generation
            await self.run_stage_4()
            
            # Stage 5: Human Verification & Deployment
            await self.run_stage_5()
            
            print("\n✅ Workflow completed successfully!")
            
        except Exception as e:
            print(f"❌ Workflow failed at stage {self.current_stage}: {e}")
            raise
    
    async def run_stage_1(self, upload_event: Dict[str, Any]):
        """Stage 1: Diagram Validation"""
        print(f"\n📋 Stage 1: Diagram Validation")
        print("-" * 30)
        
        self.current_stage = 1
        
        # Simulate diagram upload event
        await self.diagram_agent.on_gcs_upload(upload_event)
        
        # Simulate human approval
        approval_event = {
            'approved': True,
            'context': {
                'diagram': upload_event['name'],
                'validation': {'score': 85, 'confidence': 0.9},
                'description': 'Mock pattern description'
            }
        }
        await self.diagram_agent.on_human_approval(approval_event)
        
        self.workflow_state['stage_1'] = approval_event['context']
        print("✅ Stage 1 completed - Diagram validated")
    
    async def run_stage_2(self):
        """Stage 2: Document Generation"""
        print(f"\n📝 Stage 2: Document Generation")
        print("-" * 30)
        
        self.current_stage = 2
        
        # Create event from stage 1 output
        validation_event = {
            'data': json.dumps({
                'original': self.workflow_state['stage_1']['diagram'],
                'description': self.workflow_state['stage_1']['description'],
                'validation': self.workflow_state['stage_1']['validation']
            })
        }
        
        await self.doc_agent.on_diagram_validated(validation_event)
        
        self.workflow_state['stage_2'] = {
            'doc_path': f"docs/{self.workflow_state['stage_1']['diagram']}.md"
        }
        print("✅ Stage 2 completed - Documentation generated")
    
    async def run_stage_3(self):
        """Stage 3: Component Specification"""
        print(f"\n🔧 Stage 3: Component Specification")
        print("-" * 30)
        
        self.current_stage = 3
        
        # Create event from stage 2 output
        doc_event = {
            'data': json.dumps(self.workflow_state['stage_2'])
        }
        
        await self.spec_agent.on_doc_approved(doc_event)
        
        # Extract component keys properly
        components = ['comp1', 'comp2', 'comp3']  # Default mock components
        
        self.workflow_state['stage_3'] = {
            'doc_path': self.workflow_state['stage_2']['doc_path'],
            'components': components
        }
        print("✅ Stage 3 completed - Component specifications extracted")
    
    async def run_stage_4(self):
        """Stage 4: Artifact Generation"""
        print(f"\n⚙️ Stage 4: Artifact Generation")
        print("-" * 30)
        
        self.current_stage = 4
        
        # Create event from stage 3 output
        specs_event = {
            'data': json.dumps(self.workflow_state['stage_3'])
        }
        
        await self.artifact_agent.on_specs_approved(specs_event)
        
        pattern_id = self.workflow_state['stage_3']['doc_path'].split('/')[-1].replace('.md', '')
        self.workflow_state['stage_4'] = {
            'pattern_id': pattern_id,
            'artifacts': ['terraform', 'code', 'pipeline']
        }
        print("✅ Stage 4 completed - Deployment artifacts generated")
    
    async def run_stage_5(self):
        """Stage 5: Human Verification & Deployment"""
        print(f"\n👤 Stage 5: Human Verification & Deployment")
        print("-" * 30)
        
        self.current_stage = 5
        
        # Simulate verification request
        verification_event = {
            'data': json.dumps({
                'stage': 'artifacts',
                'context': self.workflow_state['stage_4']
            })
        }
        
        await self.human_agent.on_verification_request(verification_event)
        
        # Simulate human approval and deployment
        review_event = {
            'session_id': 'test_session_123',
            'decision': 'approve',
            'comments': 'All artifacts look good for deployment'
        }
        
        # Add session to human agent for testing
        self.human_agent.review_sessions['test_session_123'] = {
            'stage': 'artifacts',
            'context': self.workflow_state['stage_4']
        }
        
        await self.human_agent.on_review_complete(review_event)
        
        print("✅ Stage 5 completed - Artifacts deployed")
    
    def print_workflow_summary(self):
        """Print a summary of the completed workflow"""
        print("\n" + "=" * 60)
        print("📊 WORKFLOW SUMMARY")
        print("=" * 60)
        
        for stage, data in self.workflow_state.items():
            print(f"\n{stage.upper()}: {json.dumps(data, indent=2)}")


async def run_test_workflow():
    """Run a complete test of the EnGen workflow"""
    print("🧪 Testing EnGen Agentic AI Workflow")
    print("=" * 60)
    
    # Initialize orchestrator
    orchestrator = WorkflowOrchestrator()
    
    # Mock diagram upload event
    mock_upload_event = {
        'bucket': 'engen-uploads',
        'name': 'test-diagram-pattern-123.png',
        'timeCreated': '2025-07-28T10:00:00Z'
    }
    
    # Run the complete workflow
    await orchestrator.start_workflow(mock_upload_event)
    
    # Print summary
    orchestrator.print_workflow_summary()


def test_agent_imports():
    """Test that all agents can be imported and instantiated"""
    print("🔍 Testing Agent Imports and Instantiation")
    print("-" * 50)
    
    try:
        # Test individual agent imports
        diagram_agent = DiagramValidatorAgent()
        print("✅ DiagramValidatorAgent imported and instantiated")
        
        doc_agent = DocumentGenerationAgent()
        print("✅ DocumentGenerationAgent imported and instantiated")
        
        spec_agent = ComponentSpecificationAgent()
        print("✅ ComponentSpecificationAgent imported and instantiated")
        
        artifact_agent = ArtifactGenerationAgent()
        print("✅ ArtifactGenerationAgent imported and instantiated")
        
        human_agent = HumanVerifierAgent()
        print("✅ HumanVerifierAgent imported and instantiated")
        
        print("\n✅ All agents successfully imported and instantiated!")
        return True
        
    except Exception as e:
        print(f"❌ Failed to import/instantiate agents: {e}")
        return False


async def main():
    """Main test function"""
    print("🎯 EnGen ADK Agents - Modular Testing")
    print("=" * 60)
    
    # Test 1: Agent imports
    if not test_agent_imports():
        return
    
    print("\n")
    
    # Test 2: Complete workflow
    await run_test_workflow()
    
    print("\n🎉 All tests completed successfully!")


if __name__ == "__main__":
    # Run the test orchestrator
    asyncio.run(main())
