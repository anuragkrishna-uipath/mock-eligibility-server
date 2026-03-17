FROM python:3.9-slim
WORKDIR /app
COPY mock_mcp_http_server.py .
EXPOSE 8080
CMD ["python3", "mock_mcp_http_server.py"]
