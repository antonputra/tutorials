## How to build container image?

### Navigate to the '1-container' directory

```bash
cd tutorials/lessons/182/1-container
```

### Build container image

```bash
docker build -t <your-username>/myapp:0.1.0 .
```

### Log in to Docker Hub to upload the image

```bash
docker login --username <your-username>
```

### Push the container image to the remote repository

```bash
docker push <your-username>/myapp:0.1.0
```
