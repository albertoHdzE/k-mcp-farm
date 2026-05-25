import uuid
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from mcpgateway.db import (
    SessionLocal, EmailUser, EmailTeam, EmailTeamMember, 
    Gateway, Server, Tool, ToolMetric, ToolMetricsHourly,
    ServerMetric, utc_now
)
from mcpgateway.utils.create_slug import slugify
import random

def populate_demo_data():
    session = SessionLocal()
    try:
        # 1. Ensure Admin User exists
        admin = session.query(EmailUser).filter_by(email="admin@example.com").first()
        if not admin:
            print("Admin user not found.")
            return

        # 2. Get/Create Teams
        engineering = session.query(EmailTeam).filter_by(name="Engineering").first()
        security = session.query(EmailTeam).filter_by(name="Security").first()
        
        # 3. Create Additional Gateways
        gateways_data = [
            {
                "name": "Cloudflare",
                "url": "https://docs.mcp.cloudflare.com/sse",
                "description": "Cloudflare documentation and edge infrastructure tools",
                "tools": [
                    {"original_name": "search_docs", "description": "Search cloudflare documentation"},
                    {"original_name": "list_zones", "description": "List DNS zones"},
                    {"original_name": "purge_cache", "description": "Purge Cloudflare CDN cache"}
                ]
            },
            {
                "name": "HuggingFace",
                "url": "https://hf.co/mcp",
                "description": "AI model hub and dataset tools",
                "tools": [
                    {"original_name": "list_models", "description": "Search for machine learning models"},
                    {"original_name": "get_model_info", "description": "Get metadata for a specific model"},
                    {"original_name": "download_weights", "description": "Generate download link for model weights"}
                ]
            }
        ]

        all_new_tools = []
        for gd in gateways_data:
            gw = session.query(Gateway).filter_by(name=gd["name"]).first()
            if not gw:
                gw = Gateway(
                    id=uuid.uuid4().hex,
                    name=gd["name"],
                    slug=slugify(gd["name"]),
                    url=gd["url"],
                    description=gd["description"],
                    transport="SSE",
                    capabilities={"tools": True, "resources": False, "prompts": False},
                    created_by=admin.email,
                    team_id=engineering.id
                )
                session.add(gw)
                session.flush()

            for td in gd["tools"]:
                tool = session.query(Tool).filter_by(gateway_id=gw.id, original_name=td["original_name"]).first()
                if not tool:
                    tool = Tool(
                        id=uuid.uuid4().hex,
                        original_name=td["original_name"],
                        original_description=td["description"],
                        description=td["description"],
                        custom_name=td["original_name"],
                        custom_name_slug=slugify(td["original_name"]),
                        gateway_id=gw.id,
                        integration_type="MCP",
                        input_schema={"type": "object", "properties": {}},
                        enabled=True,
                        reachable=True,
                        team_id=gw.team_id
                    )
                    tool.name = f"{gw.slug}--{tool.custom_name_slug}"
                    session.add(tool)
                all_new_tools.append(tool)

        # 4. Updates Virtual Servers
        ai_stack = session.query(Server).filter_by(name="AI & Infosec").first()
        if not ai_stack:
            ai_stack = Server(
                id=uuid.uuid4().hex,
                name="AI & Cloud Platform",
                description="Infrastructure and AI model management",
                created_by=admin.email,
                team_id=engineering.id,
                enabled=True
            )
            session.add(ai_stack)
            session.flush()
        
        for tool in all_new_tools:
            if tool not in ai_stack.tools:
                ai_stack.tools.append(tool)

        # 5. Populate Metrics for New Tools
        now = utc_now()
        for tool in all_new_tools:
            count = random.randint(500, 1500) # Heavy usage for AI
            success = int(count * 0.99)
            failure = count - success
            
            # Simple total metric for history
            hour_start = now.replace(minute=0, second=0, microsecond=0) - timedelta(hours=1)
            hourly = ToolMetricsHourly(
                tool_id=tool.id,
                tool_name=tool.name,
                hour_start=hour_start,
                total_count=count,
                success_count=success,
                failure_count=failure,
                avg_response_time=random.uniform(0.1, 0.5),
                min_response_time=0.01,
                max_response_time=1.0,
                created_at=now
            )
            session.add(hourly)

        session.commit()
        print("Extended demo data population complete!")

    except Exception as e:
        session.rollback()
        print(f"Error: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    populate_demo_data()
