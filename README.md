# Agentic AI Projects

This repository contains implementations of agentic AI systems and workflows.

## Projects

### EnGen - Enterprise Generation Workflow

Complete ADK (Agent Development Kit) implementation for enterprise pattern generation workflow.

**Location:** `EnGen/engen_ADK_Agents.ipynb`

**Overview:**
A 5-stage agentic workflow for validating diagrams, generating documentation, extracting specifications, creating deployment artifacts, and managing human verification.

**Agents:**
1. **DiagramValidatorAgent** - Validates uploaded diagrams using Gemini Vision
2. **DocumentGenerationAgent** - Generates comprehensive documentation with RAG
3. **ComponentSpecificationAgent** - Extracts and validates component specifications
4. **ArtifactGenerationAgent** - Generates deployment artifacts (Terraform, code, pipelines)
5. **HumanVerifierAgent** - Manages human-in-the-loop verification workflow

**Features:**
- ✅ Google Cloud Platform integration (ADK, Vertex AI, Pub/Sub, BigTable, Neo4j)
- ✅ Human verification checkpoints at each stage
- ✅ Vector search and RAG for documentation
- ✅ Graph database for component relationships
- ✅ Automated artifact generation and validation
- ✅ GitHub integration for deployment
- ✅ Mock implementations for development
- ✅ Production-ready error handling and monitoring

**Tech Stack:**
- Google ADK (Agent Development Kit)
- Vertex AI (Gemini, Claude)
- Google Cloud Pub/Sub
- Google Cloud Storage
- Google Cloud BigTable
- Neo4j Graph Database
- GitHub API
- Dialogflow CX

## Getting Started

1. Install required dependencies:
   ```bash
   pip install google-adk google-cloud-pubsub google-cloud-storage google-cloud-bigtable neo4j jsonschema pydantic pyyaml
   ```

2. Set up Google Cloud credentials:
   ```bash
   gcloud auth application-default login
   ```

3. Configure environment variables for your GCP project

4. Run the notebook to see the agents in action

## Development

The current implementation uses mock services for development. Replace with actual ADK imports when deploying to production.

## License

MIT License
