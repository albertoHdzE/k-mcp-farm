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
        # 1. Ensure Admin User exists (should be there from previous step)
        admin = session.query(EmailUser).filter_by(email="admin@example.com").first()
        if not admin:
            print("Admin user not found, please run the setup first.")
            return

        # 2. Create Teams
        teams_data = [
            {"name": "Engineering", "description": "Software development and infrastructure", "visibility": "public"},
            {"name": "Marketing", "description": "Content, growth and branding", "visibility": "public"},
            {"name": "Security", "description": "Governance and audit compliance", "visibility": "public"},
        ]
        
        teams = {}
        for td in teams_data:
            team = session.query(EmailTeam).filter_by(name=td["name"]).first()
            if not team:
                team = EmailTeam(
                    id=uuid.uuid4().hex,
                    name=td["name"],
                    slug=slugify(td["name"]),
                    description=td["description"],
                    created_by=admin.email,
                    visibility=td["visibility"]
                )
                session.add(team)
                session.flush()
                # Add admin as owner
                membership = EmailTeamMember(
                    team_id=team.id,
                    user_email=admin.email,
                    role="owner",
                    joined_at=utc_now()
                )
                session.add(membership)
            teams[td["name"]] = team

        # 3. Create Gateways (MCP Servers from catalog)
        gateways_data = [
            {
                "name": "GitHub",
                "url": "https://api.githubcopilot.com/mcp",
                "description": "Version control and collaborative software development",
                "tools": [
                    {"original_name": "list_repositories", "description": "List all repositories"},
                    {"original_name": "get_repository_content", "description": "Get file content from a repository"},
                    {"original_name": "create_issue", "description": "Create a new issue"}
                ]
            },
            {
                "name": "Sentry",
                "url": "https://mcp.sentry.dev/mcp",
                "description": "Application monitoring and error tracking",
                "tools": [
                    {"original_name": "list_projects", "description": "List Sentry projects"},
                    {"original_name": "get_latest_errors", "description": "Get latest errors from a project"},
                    {"original_name": "resolve_issue", "description": "Mark an issue as resolved"}
                ]
            },
            {
                "name": "Asana",
                "url": "https://mcp.asana.com/sse",
                "description": "Task and project management platform",
                "tools": [
                    {"original_name": "get_tasks", "description": "Get tasks for a user"},
                    {"original_name": "update_task_status", "description": "Update the status of a task"},
                    {"original_name": "create_project", "description": "Create a new project"}
                ]
            },
            {
                "name": "Stripe",
                "url": "https://mcp.stripe.com/",
                "description": "Payment processing and financial infrastructure",
                "tools": [
                    {"original_name": "list_customers", "description": "List Stripe customers"},
                    {"original_name": "get_balance", "description": "Get account balance"},
                    {"original_name": "create_refund", "description": "Process a refund"}
                ]
            }
        ]

        all_tools = []
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
                    team_id=teams["Engineering"].id if gd["name"] != "Stripe" else teams["Security"].id
                )
                session.add(gw)
                session.flush()

            for td in gd["tools"]:
                tool = session.query(Tool).filter_by(gateway_id=gw.id, original_name=td["original_name"]).first()
                if not tool:
                    t_id = uuid.uuid4().hex
                    tool = Tool(
                        id=t_id,
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
                    # Force computed name
                    tool.name = f"{gw.slug}--{tool.custom_name_slug}"
                    session.add(tool)
                all_tools.append(tool)

        # 4. Create Virtual Servers
        servers_data = [
            {
                "name": "Dev Productivity Stack",
                "description": "Combined stack for development, monitoring, and task tracking",
                "team": "Engineering",
                "tools_patterns": ["github", "sentry", "asana"]
            },
            {
                "name": "Ops Portal",
                "description": "Operations and Incident Management tools",
                "team": "Engineering",
                "tools_patterns": ["sentry", "asana"]
            },
            {
                "name": "Security & Finance",
                "description": "Secure access to financial APIs for audit",
                "team": "Security",
                "tools_patterns": ["stripe"]
            }
        ]

        for sd in servers_data:
            server = session.query(Server).filter_by(name=sd["name"]).first()
            if not server:
                server = Server(
                    id=uuid.uuid4().hex,
                    name=sd["name"],
                    description=sd["description"],
                    created_by=admin.email,
                    team_id=teams[sd["team"]].id,
                    enabled=True
                )
                session.add(server)
                session.flush()
                
                # Assign tools
                for tool in all_tools:
                    for pattern in sd["tools_patterns"]:
                        if pattern in tool.name.lower():
                            server.tools.append(tool)
                            break

        # 5. Generate Metrics
        print("Generating historical metrics...")
        now = utc_now()
        for i in range(168): # Last 7 days
            hour_ts = now - timedelta(hours=i)
            hour_start = hour_ts.replace(minute=0, second=0, microsecond=0)
            
            for tool in all_tools:
                # 10 to 50 calls per hour
                count = random.randint(10, 50)
                success = random.randint(int(count * 0.9), count)
                failure = count - success
                
                # Add individual metrics for the last 2 hours (to show real-time)
                if i < 2:
                    for _ in range(count):
                        metric = ToolMetric(
                            tool_id=tool.id,
                            timestamp=hour_ts - timedelta(minutes=random.randint(0, 59)),
                            response_time=random.uniform(0.1, 2.5),
                            is_success=random.random() < 0.98
                        )
                        session.add(metric)
                
                # Add hourly aggregate
                hourly = session.query(ToolMetricsHourly).filter_by(tool_id=tool.id, hour_start=hour_start).first()
                if not hourly:
                    hourly = ToolMetricsHourly(
                        tool_id=tool.id,
                        tool_name=tool.name,
                        hour_start=hour_start,
                        total_count=count,
                        success_count=success,
                        failure_count=failure,
                        avg_response_time=random.uniform(0.5, 1.5),
                        min_response_time=0.1,
                        max_response_time=3.0,
                        created_at=now
                    )
                    session.add(hourly)

        session.commit()
        print("Demo data population complete!")
        print(f"Created {len(teams)} teams.")
        print(f"Created {len(gateways_data)} gateways.")
        print(f"Created {len(all_tools)} tools.")
        print(f"Created {len(servers_data)} virtual servers.")

    except Exception as e:
        session.rollback()
        print(f"Error populating data: {e}")
        import traceback
        traceback.print_exc()
    finally:
        session.close()

if __name__ == "__main__":
    populate_demo_data()
