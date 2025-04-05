from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from health_checker import HealthChecker

app = FastAPI()


@app.post("/check_health")
async def check_health(system_data: dict):
    try:
        checker = HealthChecker(system_data)
        health_results = await checker.check_system_health()
        health_table = checker.get_system_health_table(health_results)
        graph_image = checker.get_system_graph_image()

        html_response = f"""
        <html>
            <body>
                <h1>System Health Check Results</h1>
                <h2>Health Status Table</h2>
                <pre>{health_table}</pre>
                <h2>System Graph</h2>
                <img src="data:image/png;base64,{graph_image}" alt="System Graph">
            </body>
        </html>
        """

        return HTMLResponse(content=html_response, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
