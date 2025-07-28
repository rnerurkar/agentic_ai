# EnGen ADK Agents - Modular Implementation

This is a refactored, modular implementation of the EnGen workflow using Google's Agent Development Kit (ADK). Each agent is implemented in a separate Python file for better maintainability and testability.

## Project Structure

```
EnGen/
├── __init__.py                        # Package initialization
├── requirements.txt                   # Python dependencies
├── README.md                         # This file
├── mock_services.py                  # Mock cloud services for development
├── base_agent.py                     # Base Agent class and framework
├── diagram_validator_agent.py        # Stage 1: Diagram validation
├── document_generation_agent.py      # Stage 2: Documentation generation
├── component_specification_agent.py  # Stage 3: Component specification
├── artifact_generation_agent.py      # Stage 4: Artifact generation
├── human_verifier_agent.py          # Stage 5: Human verification
└── workflow_orchestrator.py         # Test orchestrator and workflow demo
```

## Agents Overview

### 1. DiagramValidatorAgent (Stage 1)
- **Purpose**: Validates uploaded diagrams using Gemini Vision
- **Key Features**: 
  - Pattern matching against 65 reference diagrams
  - Score-based approval (threshold: 80+)
  - Human verification checkpoint
- **Input**: GCS upload events
- **Output**: Validated diagrams with descriptions

### 2. DocumentGenerationAgent (Stage 2)
- **Purpose**: Generates comprehensive documentation from validated diagrams
- **Key Features**:
  - RAG-based content retrieval
  - Multi-section document generation
  - Template-based content assembly
- **Input**: Validated diagram events
- **Output**: Structured documentation

### 3. ComponentSpecificationAgent (Stage 3)
- **Purpose**: Extracts and validates component specifications
- **Key Features**:
  - JSON schema validation
  - Neo4j graph database storage
  - Relationship mapping
- **Input**: Approved documentation
- **Output**: Component specifications in Neo4j

### 4. ArtifactGenerationAgent (Stage 4)
- **Purpose**: Generates deployment artifacts from specifications
- **Key Features**:
  - Multi-artifact generation (Terraform, code, pipelines)
  - Template-based code generation
  - Automated validation checks
- **Input**: Approved specifications
- **Output**: Deployment-ready artifacts

### 5. HumanVerifierAgent (Stage 5)
- **Purpose**: Manages human verification workflow and final deployment
- **Key Features**:
  - Dialogflow CX integration for review sessions
  - GitHub PR creation for deployment
  - Status tracking in Neo4j
- **Input**: Verification requests from all stages
- **Output**: Approved deployments

## Quick Start

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Testing Options

#### 1. Test All Agent Compilation
```bash
python test_compilation.py
```
This will verify that all agent files compile correctly without runtime errors.

#### 2. Run Complete Workflow Test
```bash
python workflow_orchestrator.py
```
This executes the full 5-stage workflow end-to-end with mock data.

#### 3. Test Individual Agents
```python
# Test DiagramValidatorAgent
from diagram_validator_agent import DiagramValidatorAgent
agent = DiagramValidatorAgent()
print("DiagramValidatorAgent instantiated successfully!")

# Test DocumentGenerationAgent
from document_generation_agent import DocumentGenerationAgent
doc_agent = DocumentGenerationAgent()
print("DocumentGenerationAgent instantiated successfully!")

# Test other agents similarly...
```

## Testing Guide

### Compilation Testing
The `test_compilation.py` script verifies that all agent files compile correctly:

```bash
python test_compilation.py
```

**Expected Output:**
```
🧪 EnGen ADK Agents - Compilation Testing
============================================================
🔍 Testing Compilation of All Agent Files
==================================================
✅ mock_services.py - Compilation successful
✅ base_agent.py - Compilation successful  
✅ diagram_validator_agent.py - Compilation successful
✅ document_generation_agent.py - Compilation successful
✅ component_specification_agent.py - Compilation successful
✅ artifact_generation_agent.py - Compilation successful
✅ human_verifier_agent.py - Compilation successful
✅ workflow_orchestrator.py - Compilation successful
==================================================
📊 Compilation Results: 8/8 files successful
🎉 All files compiled successfully!
```

### Individual Agent Testing

#### Method 1: Import and Instantiate
```python
# Test individual agents
from diagram_validator_agent import DiagramValidatorAgent
from document_generation_agent import DocumentGenerationAgent
from component_specification_agent import ComponentSpecificationAgent
from artifact_generation_agent import ArtifactGenerationAgent
from human_verifier_agent import HumanVerifierAgent

# Instantiate agents
diagram_agent = DiagramValidatorAgent()
doc_agent = DocumentGenerationAgent()
spec_agent = ComponentSpecificationAgent()
artifact_agent = ArtifactGenerationAgent()
human_agent = HumanVerifierAgent()

print("✅ All agents instantiated successfully!")
```

#### Method 2: Test Specific Agent Methods
```python
import asyncio
from diagram_validator_agent import DiagramValidatorAgent

async def test_diagram_agent():
    agent = DiagramValidatorAgent()
    
    # Mock upload event
    mock_event = {
        'bucket': 'test-bucket',
        'name': 'test-diagram.png'
    }
    
    # Test validation (will use mock services)
    await agent.on_gcs_upload(mock_event)
    print("✅ Diagram validation test completed")

# Run test
asyncio.run(test_diagram_agent())
```

### Workflow Orchestrator Testing

#### Full Workflow Test
```bash
python workflow_orchestrator.py
```

**Expected Output:**
```
🎯 EnGen ADK Agents - Modular Testing
============================================================
🔍 Testing Agent Imports and Instantiation
--------------------------------------------------
✅ DiagramValidatorAgent imported and instantiated
✅ DocumentGenerationAgent imported and instantiated
✅ ComponentSpecificationAgent imported and instantiated
✅ ArtifactGenerationAgent imported and instantiated
✅ HumanVerifierAgent imported and instantiated
✅ All agents successfully imported and instantiated!

🧪 Testing EnGen Agentic AI Workflow
============================================================
🚀 Starting EnGen Workflow
==================================================

📋 Stage 1: Diagram Validation
------------------------------
Publishing to projects/engen-project/topics/validated-diagrams: ...
✅ Stage 1 completed - Diagram validated

📝 Stage 2: Document Generation  
------------------------------
Writing to pattern-docs/docs/test-diagram-pattern-123.png.md: ...
✅ Stage 2 completed - Documentation generated

🔧 Stage 3: Component Specification
------------------------------
✅ Stage 3 completed - Component specifications extracted

⚙️ Stage 4: Artifact Generation
------------------------------
✅ Terraform validation passed
✅ Python code validation passed
✅ Pipeline YAML validation passed
✅ Stage 4 completed - Deployment artifacts generated

👤 Stage 5: Human Verification & Deployment
------------------------------
🔔 Human review required for artifacts
✅ Stage 5 completed - Artifacts deployed

✅ Workflow completed successfully!

============================================================
📊 WORKFLOW SUMMARY
============================================================
STAGE_1: {"diagram": "test-diagram-pattern-123.png", ...}
STAGE_2: {"doc_path": "docs/test-diagram-pattern-123.png.md"}
...
🎉 All tests completed successfully!
```

#### Custom Workflow Testing
```python
import asyncio
from workflow_orchestrator import WorkflowOrchestrator

async def test_custom_workflow():
    orchestrator = WorkflowOrchestrator()
    
    # Create custom upload event
    custom_event = {
        'bucket': 'my-custom-bucket',
        'name': 'my-custom-diagram.png',
        'timeCreated': '2025-07-28T15:30:00Z'
    }
    
    # Run workflow
    await orchestrator.start_workflow(custom_event)
    
    # Print summary
    orchestrator.print_workflow_summary()

# Run custom test
asyncio.run(test_custom_workflow())
```

### Debugging and Troubleshooting

#### Enable Verbose Logging
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Run your tests with detailed logging
```

#### Test Mock Services
```python
from mock_services import storage, vertexai, pubsub

# Test storage
content = storage.read_file("test-bucket", "test-file.txt")
print(f"Storage test: {content}")

# Test Vertex AI
result = vertexai.generate_text("test-model", "test prompt")
print(f"Vertex AI test: {result}")

# Test Pub/Sub
import asyncio
asyncio.run(pubsub.publish("test-topic", b"test message"))
```

#### Check Agent Dependencies
```python
# Verify all imports work
try:
    from base_agent import Agent
    from mock_services import *
    print("✅ All dependencies imported successfully")
except ImportError as e:
    print(f"❌ Import error: {e}")
```

### Performance Testing

#### Measure Workflow Execution Time
```python
import time
import asyncio
from workflow_orchestrator import WorkflowOrchestrator

async def benchmark_workflow():
    start_time = time.time()
    
    orchestrator = WorkflowOrchestrator()
    mock_event = {'bucket': 'test', 'name': 'benchmark.png'}
    
    await orchestrator.start_workflow(mock_event)
    
    end_time = time.time()
    print(f"⏱️ Workflow completed in {end_time - start_time:.2f} seconds")

asyncio.run(benchmark_workflow())
```

### Integration Testing

#### Test with External Services (Production)
```python
# Replace mock services with real ones for integration testing
# from google.cloud import storage  # Real GCS
# from google.cloud import pubsub_v1  # Real Pub/Sub
# etc.
```

## Architecture Benefits

### 1. Modularity
- Each agent is self-contained
- Clear separation of concerns
- Easy to test individual components

### 2. Maintainability
- Single responsibility per file
- Consistent import structure
- Clear dependencies

### 3. Scalability
- Agents can be deployed independently
- Easy to add new agents or modify existing ones
- Mock services enable development without cloud dependencies

### 4. Testability
- Individual agent testing
- Comprehensive workflow orchestration
- Mock services for unit testing

## Production Deployment

### Replace Mock Services
In production, replace the mock services with actual GCP/ADK services:

```python
# Replace in each agent file:
from google.cloud import storage        # Instead of MockStorage
from google.cloud import pubsub_v1      # Instead of MockPubSub
from google.cloud import bigtable       # Instead of MockBigTable
# etc.
```

### ADK Integration
Each agent extends the base `Agent` class which would integrate with the actual ADK framework in production.

### Environment Configuration
Set up proper environment variables and service account keys for GCP services.

## Development Workflow

### 1. Setup and Validation
```bash
# Install dependencies
pip install -r requirements.txt

# Verify setup
python test_compilation.py
```

### 2. Individual Agent Development
```bash
# Edit specific agent files as needed
# Example: editing diagram_validator_agent.py

# Test specific agent compilation
python -c "from diagram_validator_agent import DiagramValidatorAgent; print('✅ Import successful')"

# Test agent instantiation
python -c "from diagram_validator_agent import DiagramValidatorAgent; agent = DiagramValidatorAgent(); print('✅ Instantiation successful')"
```

### 3. Workflow Testing
```bash
# Test complete workflow
python workflow_orchestrator.py

# Test custom scenarios
python -c "
import asyncio
from workflow_orchestrator import WorkflowOrchestrator

async def test():
    orchestrator = WorkflowOrchestrator()
    event = {'bucket': 'dev-bucket', 'name': 'dev-diagram.png'}
    await orchestrator.start_workflow(event)

asyncio.run(test())
"
```

### 4. Integration Testing
```bash
# Run all tests in sequence
python test_compilation.py && python workflow_orchestrator.py
```

### 5. Pre-Production Checklist
- [ ] All agents compile without errors (`python test_compilation.py`)
- [ ] Workflow orchestrator runs successfully (`python workflow_orchestrator.py`)
- [ ] Individual agents can be imported and instantiated
- [ ] Mock services return expected data formats
- [ ] Error handling works correctly (test with invalid inputs)
- [ ] All stages complete successfully in workflow test

## Error Handling

Each agent includes comprehensive error handling:
- Try-catch blocks for all external calls
- Monitoring integration for error logging
- Graceful failure handling
- Human verification checkpoints

## Troubleshooting

### Common Issues and Solutions

#### 1. Import Errors
```bash
# Error: ModuleNotFoundError: No module named 'xxx'
# Solution: Ensure you're in the correct directory
cd "c:\Users\rneru\OneDrive\Agentic AI\EnGen"
python -c "import diagram_validator_agent"
```

#### 2. Package Import Issues  
```bash
# Error: No module named 'EnGen'
# This happens when running from within the EnGen directory

# Solution 1: Use direct imports (recommended)
from diagram_validator_agent import DiagramValidatorAgent

# Solution 2: Add parent directory to Python path
import sys, os
sys.path.insert(0, os.path.dirname(os.getcwd()))
from EnGen import DiagramValidatorAgent

# Solution 3: Run import test
python test_imports.py
```

#### 3. JSON Parsing Errors
```bash
# Error: json.decoder.JSONDecodeError
# This is expected with mock services - they return placeholder data
# In production, real services will return valid JSON
```

#### 4. Workflow Stage Failures
```python
# Check individual stage outputs in workflow_orchestrator.py
# Each stage stores results in workflow_state dictionary
# Add debug prints: print(f"Stage data: {self.workflow_state}")
```

#### 5. Agent Instantiation Failures
```python
# Test mock services first
from mock_services import storage, vertexai
print("✅ Mock services imported")

# Then test base agent
from base_agent import Agent
agent = Agent()
print("✅ Base agent created")
```

#### 6. Async Function Errors
```python
# Always use asyncio.run() for async functions
import asyncio

async def test_function():
    # Your async code here
    pass

# Correct way to run
asyncio.run(test_function())
```

### Debugging Tips

1. **Enable Verbose Output**: Add print statements in agent methods
2. **Test Stages Individually**: Run each workflow stage separately
3. **Check Mock Data**: Verify mock services return expected formats
4. **Use Try-Catch**: Wrap test code in try-catch blocks for better error messages

### Getting Help

If you encounter issues:
1. Check the error message carefully
2. Verify all files are in the correct directory
3. Ensure Python environment is properly set up
4. Run `python test_compilation.py` to verify basic setup
5. Test with the provided examples first before modifying code

## Next Steps

1. **Replace Mock Services**: Integrate with actual GCP/ADK services
2. **Add Authentication**: Implement proper service account authentication
3. **Enhanced Testing**: Add unit tests for each agent
4. **CI/CD Pipeline**: Set up automated testing and deployment
5. **Monitoring**: Add comprehensive logging and metrics

---

## Quick Reference

### Essential Commands
```bash
# Test everything works
python test_compilation.py

# Test import patterns
python test_imports.py

# Run full workflow
python workflow_orchestrator.py

# Test individual agent import
python -c "from diagram_validator_agent import DiagramValidatorAgent; print('✅ Success')"

# Install dependencies
pip install -r requirements.txt
```

### File Structure Quick Reference
- `mock_services.py` - All mock cloud services
- `base_agent.py` - Base Agent class
- `*_agent.py` - Individual agent implementations
- `workflow_orchestrator.py` - Complete workflow test
- `test_compilation.py` - Compilation testing
- `test_imports.py` - Import pattern testing
- `requirements.txt` - Python dependencies
- `README.md` - This documentation

### Key Testing Patterns
```python
# Test agent import
from agent_name import AgentClass

# Test agent instantiation  
agent = AgentClass()

# Test async workflow
import asyncio
asyncio.run(async_function())

# Test with custom data
custom_event = {'bucket': 'test', 'name': 'test.png'}
```

**Note**: This implementation uses mock services for development. In production, replace with actual GCP/ADK service integrations.
