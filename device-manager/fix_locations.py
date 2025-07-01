with open('routers/devices.py', 'r') as f:
    content = f.read()

# Find and replace the broken locations function
broken_function = '''@router.get("/locations")
async def get_locations():
    """Get all locations"""
                cur.execute("SELECT id, name, description FROM locations ORDER BY name")
                locations = cur.fetchall()
                return [dict(location) for location in locations]'''

fixed_function = '''@router.get("/locations")
async def get_locations():
    """Get all locations"""
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id, name, description FROM locations ORDER BY name")
                locations = cur.fetchall()
                return [dict(location) for location in locations]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))'''

content = content.replace(broken_function, fixed_function)

with open('routers/devices.py', 'w') as f:
    f.write(content)

print("Fixed locations function!")
