from mcpgateway.db import SessionLocal, Gateway, Server, Tool, ToolMetric, EmailTeam, EmailUser, ToolMetricsHourly
from sqlalchemy import func

def verify():
    session = SessionLocal()
    try:
        print("--- Verification ---")
        
        user = session.query(EmailUser).filter_by(email="admin@example.com").first()
        print(f"Admin User: {user.email if user else 'NOT FOUND'}")
        
        teams = session.query(EmailTeam).count()
        print(f"Teams count: {teams}")
        
        gateways = session.query(Gateway).all()
        print(f"Gateways count: {len(gateways)}")
        for g in gateways:
            print(f"  - {g.name} ({g.slug})")
            
        tools = session.query(Tool).count()
        print(f"Tools count: {tools}")
        
        servers = session.query(Server).all()
        print(f"Virtual Servers count: {len(servers)}")
        for s in servers:
            print(f"  - {s.name} (Tools: {len(s.tools)})")
            
        metrics = session.query(ToolMetric).count()
        print(f"Metrics (total raw): {metrics}")
        
        hourly = session.query(ToolMetricsHourly).count()
        print(f"Metrics (total hourly): {hourly}")
        
        # Check last metric
        last_metric = session.query(ToolMetric).order_by(ToolMetric.timestamp.desc()).first()
        if last_metric:
            print(f"Last metric timestamp: {last_metric.timestamp}")
            
    finally:
        session.close()

if __name__ == "__main__":
    verify()
