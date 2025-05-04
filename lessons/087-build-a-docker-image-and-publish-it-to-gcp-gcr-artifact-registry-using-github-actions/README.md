# Build a Docker Image and Publish It to GCP GCR & Artifact Registry using Github Actions

[YouTube Tutorial](https://youtu.be/6dLHcnlPi_U)

## Content

- Create GitHub Repository
- Create Flask App
- Create Docker Image for Flask App
- Create Service Account in GCP
- Create GitHub Actions Docker Build and Push Workflow
- Use GitHub Actions to Push Docker to Artifact Registry
- Increment Git Tag for Each Commit and Use It for Docker Image

## Create GitHub Repository

- Go to [GitHub](https://github.com/)
- Create empty repository `lesson-087`, keep it public
- Clone repository
```bash
git clone git@github.com:antonputra/lesson-087.git
```

## Create Flask App

- Create `app.py`
- Create `requirements.txt`
- Optionally, create `.gitignore`

## Create Docker Image for Flask App

- Create `Dockerfile`
- Build docker image
```bash
docker build -t lesson-087:latest .
```
- Run docker locally
```bash
docker run -p 5000:5000 lesson-087:latest
```
- Use curl to test
```bash
curl localhost:5000/hello
```

## Create Service Account in GCP

- Create `github-actions` service account
- Create and download key for service account
- Add `Storage Admin` role to the service account, project wide permissions (fix later)

## Create GitHub Actions Docker Build and Push Workflow

- Create `.github/workflows/gcp.yml`
- Create GitHub secret `SERVICE_ACCOUNT_KEY`
- Commit and push
```bash
git add .
git commit -m 'init commit'
git push origin main
```
- Check docker image in GCR
- Fix permissions, remove wide project permissions and add to GS bucket
- Create empty commit to test CI
```bash
git commit --allow-empty -m "Trigger CI"
git push origin main
```

## Use GitHub Actions to Push Docker to Artifact Registry

- Create `images` Artifact Registry repository
- Add `github-actions` service account to `images` repo with `Artifact Registry Writer` role
- Add `gcloud auth configure-docker us-west2-docker.pkg.dev --quiet` to `Configure Docker Client` step
- Add `Push Docker Image to Artifact Registry` step
- Commit and push
```bash
git add .
git commit -m 'add step to push docker to artifact registry'
git push origin main
```

## Increment Git Tag for Each Commit and Use It for Docker Image

- Create `scripts/git_update.sh`
- Add `Automatic Tagging of Releases` step
- Update `GIT_TAG` variable to `${{ steps.increment-git-tag.outputs.git-tag }}`
- Commit and test
```bash
git add .
git commit -m 'add step to increment git tag'
git push origin main
```
- Check GitHub Tag, GCR and Artifact registry

## Links

- [Push to GCR GitHub Action](https://github.com/marketplace/actions/push-to-gcr-github-action)
- [Uploading a Docker image to GCR using Github Actions](https://medium.com/mistergreen-engineering/uploading-a-docker-image-to-gcr-using-github-actions-92e1cdf14811)
- [Using Github Actions to Build and Push Images to Google Container Registry](http://acaird.github.io/computers/2020/02/11/github-google-container-cloud-run)
- [Creating a CI/CD environment for serverless containers on Cloud Run with GitHub Actions](https://cloud.google.com/community/tutorials/cicd-cloud-run-github-actions)
- [Granting permissions](https://cloud.google.com/artifact-registry/docs/transition/changes-gcp#permissions)

## Clean Up

- Delete `github-actions` service account
- Delete `lesson-087` GCR repository
- Delete `artifacts.devopsbyexample-325402.appspot.com` GS bucket
- Delete `images` artifact repository
