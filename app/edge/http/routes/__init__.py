# Endpoints package
import importlib
import os
import pkgutil
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

def register_routes(app: FastAPI):
    # Serve uploads directory so snapshot images are accessible via URL
    uploads_path = "uploads"
    os.makedirs(uploads_path, exist_ok=True)
    app.mount("/uploads", StaticFiles(directory=uploads_path), name="uploads")

    package_name = __name__  # app.edge.http.routes
    package = importlib.import_module(package_name)

    for _, module_name, _ in pkgutil.iter_modules(package.__path__):
        if not module_name.endswith("_route"):
            continue

        module = importlib.import_module(f"{package_name}.{module_name}")

        if not hasattr(module, "router"):
            continue

        prefix = "/" + module_name.replace("_route", "")
        app.include_router(
            module.router,
            prefix=f"/api/v1{prefix}",
            tags=[prefix.strip("/")]
        )
