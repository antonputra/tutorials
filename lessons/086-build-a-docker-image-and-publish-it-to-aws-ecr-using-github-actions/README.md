# Build a Docker Image and Publish It to AWS ECR using Github Actions

[YouTube Tutorial](https://youtu.be/Hv5UcBYseus)

## Content
This guide contains instructions on how to:

- Create GitHub Repository
- Create Golang App
- Create Dockerfile for Golang
- Create GitHub Actions Workflow
- Create AWS ECR Repository
- Create AWS IAM User, Policy, and Group
- Test GitHub Actions
- Add Automatic Tagging of Releases

## Create GitHub Repository

- Create GitHub repo `lesson-086`
- Clone repository

```bash
git clone git@github.com:antonputra/lesson-086.git
```

- Initialize the Go module
```bash
go mod init github.com/antonputra/lesson-086
```

- Create `main.go` file

- Format the code and run it
```bash
# go install golang.org/x/tools/cmd/goimports@latest
go mod tidy
goimports -w .
go run main.go
```

## Create Dockerfile for Golang

- Create `Dockerfile`

## Create GitHub Actions Workflow

- Create `.github/workflows/main.yml` file, use `latest` for `IMAGE_TAG`

## Create AWS ECR Repository

- Go to AWS console, search for `ecr`
- Create private ECR repository `lesson-086`

## Create AWS IAM User, Policy, and Group

- Create IAM Policy `AllowPushPullPolicy`
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "GetAuthorizationToken",
      "Effect": "Allow",
      "Action": [
        "ecr:GetAuthorizationToken"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "ecr:BatchGetImage",
        "ecr:BatchCheckLayerAvailability",
        "ecr:CompleteLayerUpload",
        "ecr:GetDownloadUrlForLayer",
        "ecr:InitiateLayerUpload",
        "ecr:PutImage",
        "ecr:UploadLayerPart"
      ],
      "Resource": [
        "arn:aws:ecr:us-east-1:424432388155:repository/lesson-086"
      ]
    }
  ]
}
```

- Create `push-pull-images` IAM Group and attach `AllowPushPullPolicy` IAM Policy

- Create user `github-actions` and place it to `push-pull-images` IAM Group

## Test GitHub Actions

- Create initial commit
```bash
git add .
git commit -m 'init commit'
git push origin main
```

- Check ECR repository

## Add Automatic Tagging of Releases

- Create `build/git_update.sh` script

- Make a change and push to remote branch from `main`

- Create a new branch `aputra`, make a change, update `patch` -> `major` and push

## Links

- [Workflow syntax for GitHub Actions](https://docs.github.com/en/actions/learn-github-actions/workflow-syntax-for-github-actions)
- [Metadata syntax for GitHub Actions](https://docs.github.com/en/actions/creating-actions/metadata-syntax-for-github-actions)

## Clean Up

- Delete `github-actions` AWS IAM User
- Delete `AllowPushPullPolicy` AWS IAM Policy
- Delete `push-pull-images` AWS IAM Group
