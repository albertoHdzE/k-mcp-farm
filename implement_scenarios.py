import uuid
import json
from sqlalchemy.orm import Session
from mcpgateway.db import (
    SessionLocal, EmailUser, EmailTeam, EmailTeamMember, 
    Gateway, Server, Tool, Resource, Prompt, utc_now
)
from mcpgateway.utils.create_slug import slugify

def implement_scenarios():
    session = SessionLocal()
    try:
        # 1. Setup Admin and Team
        admin = session.query(EmailUser).filter_by(email="admin@example.com").first()
        if not admin:
            # Create admin if not exists (for tests/demo)
            admin = EmailUser(email="admin@example.com", is_active=True, is_admin=True)
            session.add(admin)
            session.flush()

        team = session.query(EmailTeam).filter_by(name="Scenario Demo").first()
        if not team:
            team = EmailTeam(
                id=uuid.uuid4().hex,
                name="Scenario Demo",
                slug=slugify("Scenario Demo"),
                description="Team for demonstrating MCP scenarios",
                created_by=admin.email,
                visibility="public"
            )
            session.add(team)
            session.flush()
            
            membership = EmailTeamMember(
                team_id=team.id,
                user_email=admin.email,
                role="owner",
                joined_at=utc_now()
            )
            session.add(membership)
            session.flush()

        # 2. Scenario: Agent to call an external API (REST Tool)
        api_tool = session.query(Tool).filter_by(name="external_api_post_lookup").first()
        if not api_tool:
            api_tool = Tool(
                id=uuid.uuid4().hex,
                original_name="get_post",
                custom_name="external_api_post_lookup",
                custom_name_slug="external-api-post-lookup",
                name="external_api_post_lookup",
                description="Fetch a post from an external JSON API",
                integration_type="REST",
                base_url="https://jsonplaceholder.typicode.com",
                path_template="/posts/{id}",
                request_type="GET",
                input_schema={
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer", "description": "The ID of the post to fetch"}
                    },
                    "required": ["id"]
                },
                team_id=team.id,
                owner_email=admin.email,
                visibility="public"
            )
            session.add(api_tool)
            print("Registered External API scenario tool.")

        # 3. Scenario: Agent to get a knowledge context (Resource)
        resource = session.query(Resource).filter_by(uri="file://knowledge_base.md").first()
        if not resource:
            with open("knowledge_base.md", "r") as f:
                content = f.read()
            resource = Resource(
                id=uuid.uuid4().hex,
                uri="file://knowledge_base.md",
                name="System Knowledge Base",
                description="Knowledge context for the AI agent",
                text_content=content,
                mime_type="text/markdown",
                team_id=team.id,
                owner_email=admin.email,
                visibility="public"
            )
            session.add(resource)
            print("Registered Knowledge Context scenario resource.")

        # 4. Scenario: Agent to call a prompt template
        prompt = session.query(Prompt).filter_by(name="welcome_prompt").first()
        if not prompt:
            prompt = Prompt(
                id=uuid.uuid4().hex,
                original_name="welcome_prompt",
                custom_name="welcome_prompt",
                custom_name_slug="welcome-prompt",
                name="welcome_prompt",
                description="A welcome prompt template",
                template="Hello {name}, welcome to ContextForge! How can I assist you with your {task} today?",
                argument_schema={
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "task": {"type": "string"}
                    },
                    "required": ["name", "task"]
                },
                team_id=team.id,
                owner_email=admin.email,
                visibility="public"
            )
            session.add(prompt)
            print("Registered Prompt Template scenario.")

        # 5. Scenario: Agent to call a utility or function
        # We'll use a REST tool that calls a mock utility echo service
        util_tool = session.query(Tool).filter_by(name="utility_echo").first()
        if not util_tool:
            util_tool = Tool(
                id=uuid.uuid4().hex,
                original_name="echo",
                custom_name="utility_echo",
                custom_name_slug="utility-echo",
                name="utility_echo",
                description="A utility function that echoes back the input",
                integration_type="REST",
                base_url="https://postman-echo.com",
                path_template="/get",
                query_mapping={"text": "message"},
                request_type="GET",
                input_schema={
                    "type": "object",
                    "properties": {
                        "message": {"type": "string", "description": "The message to echo"}
                    },
                    "required": ["message"]
                },
                team_id=team.id,
                owner_email=admin.email,
                visibility="public"
            )
            session.add(util_tool)
            print("Registered Utility Function scenario tool.")

        # 6. Scenario: Agent calling another agent (A2A)
        # For this we'll create an A2A agent entry
        from mcpgateway.db import A2AAgent
        a2a_agent = session.query(A2AAgent).filter_by(name="Assistant Agent").first()
        if not a2a_agent:
            a2a_agent = A2AAgent(
                id=uuid.uuid4().hex,
                name="Assistant Agent",
                slug="assistant-agent",
                description="Secondary agent for sub-tasks",
                endpoint_url="http://localhost:4444/a2a/assistant",
                agent_type="assistant",
                visibility="public",
                team_id=team.id,
                owner_email=admin.email
            )
            session.add(a2a_agent)
            print("Registered A2A Agent scenario.")

        # 7. Scenario: A/B Testing Prompt
        # We'll register two versions of a prompt
        prompt_a = session.query(Prompt).filter_by(name="query_refinement_a").first()
        if not prompt_a:
            prompt_a = Prompt(
                id=uuid.uuid4().hex,
                original_name="query_refinement_a",
                custom_name="query_refinement_v1",
                custom_name_slug="query-refinement-v1",
                name="query_refinement_a",
                template="Refine this query: {query}",
                argument_schema={"type": "object", "properties": {"query": {"type": "string"}}},
                team_id=team.id,
                owner_email=admin.email,
                visibility="public"
            )
            session.add(prompt_a)
        
        prompt_b = session.query(Prompt).filter_by(name="query_refinement_b").first()
        if not prompt_b:
            prompt_b = Prompt(
                id=uuid.uuid4().hex,
                original_name="query_refinement_b",
                custom_name="query_refinement_v2",
                custom_name_slug="query-refinement-v2",
                name="query_refinement_b",
                template="Please provide a detailed refinement for the following user request: {query}",
                argument_schema={"type": "object", "properties": {"query": {"type": "string"}}},
                team_id=team.id,
                owner_email=admin.email,
                visibility="public"
            )
            session.add(prompt_b)
            print("Registered A/B Testing Prompts.")

        session.commit()
        print("\nAll scenario components registered successfully!")

    except Exception as e:
        session.rollback()
        print(f"Error implementing scenarios: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    implement_scenarios()
