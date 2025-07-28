"""
Base classes for ADK framework
Contains the abstract Agent class and basic framework components
"""

import asyncio
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from mock_services import MockMonitoring


class Agent:
    """Base ADK Agent class"""
    def __init__(self):
        self.monitoring = MockMonitoring()
    
    async def on_event(self, event):
        """Default event handler"""
        pass

    async def request_human_verification(self, stage: str, context: dict):
        """Standard human verification request"""
        from mock_services import pubsub
        import json
        await pubsub.publish(
            "projects/engen-project/topics/human-verification",
            data=json.dumps({"stage": stage, "context": context}).encode()
        )
