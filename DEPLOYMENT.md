# Docker Deployment

This project runs as a Dockerized FastAPI app that serves the React frontend and API from one process. The container installs the native OCR dependency `tesseract-ocr` and starts Uvicorn on the `$PORT` provided by Render or Railway.

## Build Locally

```bash
docker build -t ai-prescription-reader .
docker run --env-file .env -p 8000:8000 ai-prescription-reader
```

Open `http://localhost:8000`.

## Push To Docker Hub

```bash
docker login
docker tag ai-prescription-reader YOUR_DOCKERHUB_USERNAME/ai-prescription-reader:latest
docker push YOUR_DOCKERHUB_USERNAME/ai-prescription-reader:latest
```

## Render

1. Create a new **Web Service**.
2. Choose **Deploy an existing image from a registry** or connect this Git repo and select Docker.
3. Use image `YOUR_DOCKERHUB_USERNAME/ai-prescription-reader:latest` if deploying from Docker Hub.
4. Add environment variables from `.env.example`.
5. For MongoDB Atlas, set `MONGODB_URI` to your Atlas connection string.

Render supplies the `PORT` variable automatically. The Dockerfile already uses it.

## Railway

1. Create a new Railway project.
2. Deploy from this repo or from the Docker image.
3. Add environment variables from `.env.example`.
4. Set `MONGODB_URI` to a Railway MongoDB plugin URL or MongoDB Atlas URL.

Railway supplies the `PORT` variable automatically. The Dockerfile already uses it.

## Notes

- Do not commit `.env`; use platform environment variables instead.
- Uploaded prescriptions and generated reports are written to `outputs/`. On hosted free/ephemeral services, those files may disappear after restart unless you attach persistent storage.
- `database/users.db` is ignored by Docker because local SQLite data should not be baked into the production image.
