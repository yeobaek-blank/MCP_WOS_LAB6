# main.py

from mcp_server import get_app

app = get_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8989, debug=True)
