from langchain_core.tools import tool

@tool
def get_ip_activity_history(ip: str) -> list[str]:
    """query the activity history of a given IP address from the global log cache"""
    return [
        f"{ip} - - GET /login.html HTTP/1.1 200 OK",
        f"{ip} - - GET /api/v1/users HTTP/1.1 401 Unauthorized",
        f"{ip} - - POST /wp-login.php HTTP/1.1 401 Unauthorized",
        f"{ip} - - POST /etc/passwd HTTP/1.1 401 Unauthorized",
    ]