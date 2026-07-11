from fastmcp import FastMCP 
import os 
import sqlite3

DB_PATH         = os.path.join(os.path.dirname(__file__), "expenses.db")
CATEGORIES_PATH = os.path.join(os.path.dirname(__file__), "categories.json")

mcp = FastMCP("Expense Tracker")

def init_db():
    with sqlite3.connect(DB_PATH) as cursor:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS expenses(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                subcategory TEXT DEFAULT '',
                note TEXT DEFAULT ''          
            )
        """)

init_db()

@mcp.tool()
def add_expense(date, amount, category, subcategory='', note=''):
    """Add a new expense entry to the database"""
    with sqlite3.connect(DB_PATH) as cursor:
        cur = cursor.execute(
            "INSERT INTO expenses(date, amount, category, subcategory, note) VALUES(?,?,?,?,?)",
            (date, amount, category, subcategory, note)
        )
        return {"status":"ok", "id":cur.lastrowid}
    
@mcp.tool()
def list_expenses(start_date, end_date):
    with sqlite3.connect(DB_PATH) as cursor:
        """List expense entries within an inclusive date range"""
        cur = cursor.execute("""
                             SELECT id, date, amount, category, subcategory, note 
                             FROM expenses 
                             WHERE date between ? AND ?
                             ORDER BY id ASC
                             """, (start_date, end_date))
        cols = [d[0] for d in cur.description]
        return [dict(zip(cols, r)) for r in cur.fetchall()]


@mcp.tool()
def summarize(start_date, end_date, category=None):
    with sqlite3.connect(DB_PATH) as cursor:
        """Summarize expenses by category within an inclusive date range"""
        cur = cursor.execute("""
                             SELECT category, SUM(amount) AS total_amount 
                             FROM expenses 
                             WHERE date BETWEEN ? AND ?
                             """)
        params = [start_date, end_date]
        if category:
            query += " AND cateory = ?"
            params.append(category)
        query +=  " GROUP BY category ORDER BY category ASC"

        cur = cursor.execute(query, params)

        cols = [d[0] for d in cur.description]
        return [dict(zip(cols, r)) for r in cur.fetchall()]


@mcp.resource("expense://categories", mime_type="application/json")
def categories():
    # Read fresh each time so you can edit the file without restarting
    with open(CATEGORIES_PATH, "r", encoding="utf-8") as f:
        return f.read()
    
# Start the server
if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8000)

#----------------------------------------------------------------------
# from fastmcp import FastMCP
# import random
# import json

# # Create fast mcp server instance
# mcp = FastMCP("Simple Calculator Server")

# # Tool: Add two numbers 
# @mcp.tool
# def add(a: int, b: int) -> int:
#     """
#         Add two numbers together 
#         Args: 
#             a: First number 
#             b: Second number 

#         Returns:
#             The sum of a and b
#     """
#     return a+b

# # Tool: Generate a random number 
# @mcp.tool
# def random_number(min_val: int=1, max_val: int=100) -> int:
#     """ Generate a random number within a range 

#         Args:
#             min_val: Minimum value (default = 1)
#             max_val: Maximum value (default = 100) 

#         Returns:
#             A random integer between min_val and max_val
#     """
#     return random.randint(min_val, max_val)

# # Resource: Server information
# @mcp.resource("info://server")
# def server_into() -> str:
#     """Get information about this server"""
#     info = {
#         "name": "Simple Calculator server",
#         "version": "1.0.0",
#         "description": "A basic MCP server with math tools",
#         "tools": ["add", "random_number"],
#         "author": "Tarun Kumar" 
#     }
#     return json.dumps(info, indent=2)

# # Start the server
# if __name__ == "__main__":
#     mcp.run(transport="http", host="0.0.0.0", port=8000)
