"""
Mock services for ADK framework development
This module provides mock implementations of various cloud services
"""

import json
from typing import Dict, Any, List, Optional


class MockMonitoring:
    """Mock monitoring for development"""
    async def log_error(self, message: str):
        print(f"ERROR: {message}")


class MockStorage:
    """Mock storage for development"""
    @staticmethod
    def read_file(bucket: str, path: str) -> bytes:
        # Return different mock content based on path
        if "prompt" in path:
            return b"Mock prompt template for {path}"
        elif "template" in path:
            return b'{"sections": [{"id": "overview", "title": "Overview"}]}'
        elif "schema" in path:
            return b'{"type": "object", "properties": {"components": {"type": "object"}}}'
        elif "example" in path:
            return b'{"components": {"service1": {"id": "service1", "type": "service"}}}'
        return b"mock file content"
    
    @staticmethod
    def write_file(bucket: str, path: str, content: str):
        print(f"Writing to {bucket}/{path}: {content[:100]}...")


class MockVertexAI:
    """Mock Vertex AI for development"""
    @staticmethod
    def analyze_image(model: str, image: bytes, prompt: str, reference_images: List[bytes] = None, params: Dict = None) -> Dict:
        return {"score": 85, "confidence": 0.9, "matches": ["pattern_1", "pattern_3"]}
    
    @staticmethod
    def generate_text(model: str, prompt: str, image: bytes = None, response_format: str = None, params: Dict = None) -> str:
        if response_format == "json":
            return '{"components": [{"id": "comp1", "type": "service"}], "relationships": []}'
        return "Generated text content based on the prompt"
    
    @staticmethod
    def vector_search(index: str, query: str, filter: str = None, num_results: int = 3) -> List:
        class MockResult:
            def __init__(self, content):
                self.content = content
        return [MockResult(f"Search result {i}") for i in range(num_results)]


class MockPubSub:
    """Mock Pub/Sub for development"""
    @staticmethod
    async def publish(topic: str, data: bytes):
        print(f"Publishing to {topic}: {data.decode()[:100]}...")


class MockBigTable:
    """Mock BigTable for development"""
    @staticmethod
    def get_row(instance_id: str, table_id: str, row_key: str):
        class MockCell:
            def __init__(self, value):
                self.value = value
        class MockRow:
            def __init__(self):
                self.cells = {"prompt": [MockCell(b"Mock prompt template")], "template": [MockCell(b"Mock template content")]}
        return MockRow()


class MockNeo4j:
    """Mock Neo4j for development"""
    @staticmethod
    def Driver(uri: str, auth: tuple):
        return MockNeo4jDriver()
    
    @staticmethod
    def secret(name: str) -> str:
        return f"mock_{name}"


class MockNeo4jDriver:
    def session(self):
        return MockNeo4jSession()


class MockNeo4jSession:
    def run(self, query: str, **kwargs):
        class MockRecord:
            def __init__(self, data):
                self.data = data
            def __getitem__(self, key):
                return self.data.get(key, f"mock_{key}")
        class MockResult:
            def single(self):
                return MockRecord({"c": {"type": "service"}, "rels": [], "related": []})
            def __iter__(self):
                return iter([MockRecord({"id": f"comp_{i}"}) for i in range(3)])
        return MockResult()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


class MockGitHub:
    """Mock GitHub for development"""
    @staticmethod
    def create_pr(repo: str, title: str, branch: str, files: Dict) -> str:
        return f"https://github.com/mock/{repo}/pull/123"


class MockDialogflow:
    """Mock Dialogflow for development"""
    @staticmethod
    def create_session(agent_id: str, parameters: Dict) -> str:
        return f"session_{hash(str(parameters))}"


# Initialize mock services as global instances
storage = MockStorage()
vertexai = MockVertexAI()
pubsub = MockPubSub()
bigtable = MockBigTable()
neo4j = MockNeo4j()
github = MockGitHub()
dialogflow = MockDialogflow()
