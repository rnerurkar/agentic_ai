"""
Human Verifier Agent - Stage 5
Manages human verification workflow
"""

import json
from typing import Dict, Any, List, Optional
from base_agent import Agent
from mock_services import storage, pubsub, neo4j, github, dialogflow


class HumanVerifierAgent(Agent):
    """Stage 5: Manages human verification workflow"""
    
    def __init__(self):
        super().__init__()
        self.review_sessions = {}

    async def on_verification_request(self, event):
        """Handle verification requests from all agents"""
        # Handle both dict and object with data attribute
        if hasattr(event, 'data'):
            data = json.loads(event.data)
        elif isinstance(event, dict) and 'data' in event:
            data = json.loads(event['data'])
        else:
            data = event
            
        session_id = self.create_review_session(data['stage'], data['context'])
        self.review_sessions[session_id] = data

        # Notify human via preferred channel
        await self.notify_reviewer(data['stage'], session_id, data['context'])

    async def on_review_complete(self, event):
        """Process human decisions"""
        session_id = event['session_id']
        decision = event['decision']
        comments = event.get('comments', "")

        if session_id in self.review_sessions:
            context = self.review_sessions[session_id]

            if decision == "approve":
                # Trigger next stage
                await pubsub.publish(
                    f"projects/engen-project/topics/{context['stage']}-approved",
                    data=json.dumps(context).encode()
                )

                # Final deployment if last stage
                if context['stage'] == "artifacts":
                    await self.deploy_artifacts(context.get('pattern_id'))
            else:
                await self.handle_rejection(context['stage'], context, comments)

    async def deploy_artifacts(self, pattern_id: str):
        """Deploy approved artifacts"""
        if not pattern_id:
            return
            
        artifacts_content = storage.read_file("generated-artifacts", f"{pattern_id}.json").decode()
        artifacts = json.loads(artifacts_content) if artifacts_content else {}

        # Create GitHub PR
        pr_url = github.create_pr(
            repo="engen-patterns",
            title=f"Pattern {pattern_id} Implementation",
            branch=f"pattern/{pattern_id}",
            files=artifacts
        )

        # Update deployment status
        with neo4j.Driver(neo4j.secret("neo4j-uri"), auth=(neo4j.secret("neo4j-user"), neo4j.secret("neo4j-password"))).session() as session:
            session.run("""
                MERGE (p:Pattern {id: $id})
                SET p.status = 'deployed',
                    p.pr_url = $pr_url,
                    p.deployed_at = datetime()
            """, id=pattern_id, pr_url=pr_url)

        # Notify stakeholders
        await self.notify_deployment(pattern_id, pr_url)

    def create_review_session(self, stage: str, context: dict) -> str:
        """Create Dialogflow CX session"""
        return dialogflow.create_session(
            agent_id="engen-review-agent",
            parameters={
                "stage": stage,
                "context": json.dumps(context)
            }
        )

    async def notify_reviewer(self, stage: str, session_id: str, context: dict):
        """Notify human reviewer"""
        print(f"🔔 Human review required for {stage}")
        print(f"Session ID: {session_id}")
        print(f"Context: {json.dumps(context, indent=2)}")

    async def handle_rejection(self, stage: str, context: dict, comments: str):
        """Handle rejection with feedback"""
        print(f"❌ {stage} rejected: {comments}")

    async def notify_deployment(self, pattern_id: str, pr_url: str):
        """Notify stakeholders of deployment"""
        print(f"🚀 Pattern {pattern_id} deployed successfully!")
        print(f"📋 PR URL: {pr_url}")
