"""Fix REST tool URLs so they are invocable via tool_service."""
from mcpgateway.db import SessionLocal, Tool

def fix_tool_urls():
    session = SessionLocal()
    try:
        # Fix external API tool - set url so path substitution works
        api_tool = session.query(Tool).filter(
            Tool.name.in_(["external_api_post_lookup", "external-api-post-lookup"])
        ).first()
        if api_tool:
            api_tool.url = "https://jsonplaceholder.typicode.com/posts/{id}"
            api_tool.base_url = "https://jsonplaceholder.typicode.com"
            api_tool.path_template = "/posts/{id}"
            api_tool.request_type = "GET"
            print(f"Fixed url for: {api_tool.name}")
        else:
            print("external_api_post_lookup tool not found")

        # Fix utility echo tool - set url so it can make GET requests
        util_tool = session.query(Tool).filter(
            Tool.name.in_(["utility_echo", "utility-echo"])
        ).first()
        if util_tool:
            util_tool.url = "https://postman-echo.com/get"
            util_tool.base_url = "https://postman-echo.com"
            util_tool.path_template = "/get"
            util_tool.request_type = "GET"
            print(f"Fixed url for: {util_tool.name}")
        else:
            print("utility_echo tool not found")

        session.commit()
        print("\nTool URLs updated. Re-running test_scenarios.py to verify...")
    except Exception as e:
        session.rollback()
        print(f"Error: {e}")
        raise
    finally:
        session.close()

if __name__ == "__main__":
    fix_tool_urls()
