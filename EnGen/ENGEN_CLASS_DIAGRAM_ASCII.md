# EnGen Agent Framework Class Diagram (ASCII)

## Class Hierarchy and Relationships

```
                                    ┌─────────────────────┐
                                    │        Agent        │
                                    │    (base_agent)     │
                                    │ ─────────────────── │
                                    │ +monitoring: Mock   │
                                    │ +agent_id: str      │
                                    │ +version: str       │
                                    │ +status: str        │
                                    │ ─────────────────── │
                                    │ +on_event()         │
                                    │ +request_human_     │
                                    │  verification()     │
                                    └─────────────────────┘
                                             △
                                             │ extends
                  ┌──────────────────────────┼──────────────────────────┐
                  │                          │                          │
                  │                          │                          │
    ┌─────────────────────┐    ┌─────────────────────┐    ┌─────────────────────┐
    │DiagramValidatorAgent│    │DocumentGenerationAgt│    │ComponentSpecAgt     │
    │   (Stage 1)         │    │   (Stage 2)         │    │   (Stage 3)         │
    │ ─────────────────── │    │ ─────────────────── │    │ ─────────────────── │
    │ +publisher: PubSub  │    │ +doc_templates: dict│    │ +driver: Neo4jDriver│
    │ +topic_path: str    │    │ +quality_threshold  │    │ +schema_validator   │
    │ +approval_threshold │    │ +generation_metrics │    │ +extraction_engine  │
    │ +max_ref_patterns   │    │ ─────────────────── │    │ +graph_manager      │
    │ ─────────────────── │    │ +on_diagram_valid() │    │ ─────────────────── │
    │ +on_gcs_upload()    │    │ +generate_docs()    │    │ +on_docs_approved() │
    │ +validate_diagram() │    │ +enhance_with_rag() │    │ +extract_components │
    │ +score_similarity() │    │ +apply_templates()  │    │ +validate_schema()  │
    │ +get_ref_patterns() │    │ +quality_check()    │    │ +store_in_graph()   │
    │ +decide_approval()  │    │ +format_document()  │    │ +build_relationships│
    └─────────────────────┘    └─────────────────────┘    └─────────────────────┘
                  │                          │                          │
                  │ publishes to             │ publishes to             │ publishes to
                  ▼                          ▼                          ▼
    ┌─────────────────────┐    ┌─────────────────────┐    ┌─────────────────────┐
    │ArtifactGenerationAgt│    │ HumanVerifierAgent  │    │WorkflowOrchestrator │
    │   (Stage 4)         │    │   (Stage 5)         │    │   (Orchestrator)    │
    │ ─────────────────── │    │ ─────────────────── │    │ ─────────────────── │
    │ +driver: Neo4jDriver│    │ +verification_queue │    │ +diagram_agent      │
    │ +supported_artifacts│    │ +review_sessions    │    │ +doc_agent          │
    │ +validation_thresh  │    │ +notification_chan  │    │ +spec_agent         │
    │ +template_cache     │    │ +deployment_manager │    │ +artifact_agent     │
    │ +generation_metrics │    │ ─────────────────── │    │ +human_agent        │
    │ ─────────────────── │    │ +on_verification_   │    │ +workflow_state     │
    │ +on_specs_approved()│    │  request()          │    │ +current_stage      │
    │ +generate_artifacts │    │ +create_review_     │    │ ─────────────────── │
    │ +validate_artifacts │    │  session()          │    │ +start_workflow()   │
    │ +generate_from_     │    │ +notify_reviewers() │    │ +run_stage_1()      │
    │  template()         │    │ +handle_approval()  │    │ +run_stage_2()      │
    │ +get_pattern_       │    │ +handle_rejection() │    │ +run_stage_3()      │
    │  components()       │    │ +deploy_artifacts() │    │ +run_stage_4()      │
    └─────────────────────┘    └─────────────────────┘    └─────────────────────┘
```

## Mock Services Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              MOCK SERVICES                                     │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌─────────────────────┐  ┌─────────────────────┐  ┌─────────────────────┐     │
│  │   MockMonitoring    │  │   MockStorage       │  │   MockVertexAI      │     │
│  │ ─────────────────── │  │ ─────────────────── │  │ ─────────────────── │     │
│  │ +log_error()        │  │ +read_file()        │  │ +analyze_image()    │     │
│  │ +log_event()        │  │ +write_file()       │  │ +generate_text()    │     │
│  │ +log_warning()      │  │ +list_files()       │  │ +vector_search()    │     │
│  └─────────────────────┘  └─────────────────────┘  └─────────────────────┘     │
│                                                                                 │
│  ┌─────────────────────┐  ┌─────────────────────┐  ┌─────────────────────┐     │
│  │    MockPubSub       │  │   MockBigTable      │  │    MockNeo4j        │     │
│  │ ─────────────────── │  │ ─────────────────── │  │ ─────────────────── │     │
│  │ +publish()          │  │ +get_row()          │  │ +Driver()           │     │
│  │ +subscribe()        │  │ +put_row()          │  │ +session()          │     │
│  │ +create_topic()     │  │ +scan_table()       │  │ +run()              │     │
│  └─────────────────────┘  └─────────────────────┘  └─────────────────────┘     │
│                                                                                 │
│  ┌─────────────────────┐  ┌─────────────────────┐                              │
│  │    MockGitHub       │  │  MockDialogflow     │                              │
│  │ ─────────────────── │  │ ─────────────────── │                              │
│  │ +create_pr()        │  │ +create_session()   │                              │
│  │ +merge_pr()         │  │ +detect_intent()    │                              │
│  │ +get_repo()         │  │ +fulfill_intent()   │                              │
│  └─────────────────────┘  └─────────────────────┘                              │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## Key Relationships Summary

### Inheritance (IS-A)
- `DiagramValidatorAgent` IS-A `Agent`
- `DocumentGenerationAgent` IS-A `Agent`
- `ComponentSpecificationAgent` IS-A `Agent`
- `ArtifactGenerationAgent` IS-A `Agent`
- `HumanVerifierAgent` IS-A `Agent`

### Composition (HAS-A)
- `WorkflowOrchestrator` HAS-A all 5 agent instances
- Each agent HAS-A `MockMonitoring` instance
- Agents HAS-A specific service clients (Neo4j, PubSub, etc.)

### Dependencies (USES)
- All agents USE mock services for external integrations
- `ComponentSpecificationAgent` USES `MockNeo4j` for graph database
- `ArtifactGenerationAgent` USES `MockBigTable` for template storage
- `DocumentGenerationAgent` USES `MockVertexAI` for text generation
- `DiagramValidatorAgent` USES `MockVertexAI` for image analysis
- `HumanVerifierAgent` USES `MockGitHub` and `MockDialogflow`

### Communication Patterns
- **Event-Driven**: Agents communicate through pub/sub events
- **Sequential Processing**: Stage 1 → Stage 2 → Stage 3 → Stage 4 → Stage 5
- **Human-in-the-Loop**: Any stage can request human verification
- **Orchestrated**: `WorkflowOrchestrator` manages the complete pipeline

### Workflow Flow
```
Diagram Upload → [Stage 1: DiagramValidator] → [Stage 2: DocumentGeneration] → 
[Stage 3: ComponentSpecification] → [Stage 4: ArtifactGeneration] → 
[Stage 5: HumanVerifier] → Deployment
```

### Error Handling and Quality Gates
```
Each Stage:
├── Automated Processing
├── Quality Assessment
├── Threshold Check
├── Auto-Approve (if high quality) OR Human Review (if uncertain)
└── Continue to Next Stage OR Reject with Feedback
```

This ASCII diagram shows the complete EnGen agent framework with clear inheritance from the base Agent class, sequential workflow processing, and comprehensive mock service integration for development and testing.
