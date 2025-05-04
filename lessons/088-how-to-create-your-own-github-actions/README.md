# How to Create Your Own GitHub Actions?

[YouTube Tutorial](https://youtu.be/jwdG6D-AB1k)

## Content

- Demo
- Build JavaScript GitHub Action
- Test JavaScript GitHub Action


## Build JavaScript GitHub Action
- Create GitHub repository `increment-git-tag` for JavaScript GitHub Action. Keep it public to allow other repositories to use this action. Also, add a README.md file, gitignore, and select MIT Licence.

- Clone repository
```bash
git clone git@github.com:antonputra/increment-git-tag.git
```

- Initialize the project and install dependencies
```bash
cd increment-git-tag
npm init -y
npm i @actions/core
npm i @actions/exec
```

- Open Project
```bash
code .
```

- Create `action.yml`
- Create `index.js`

- Install vercel/ncc
```bash
npm i -g @vercel/ncc
```

- Compile JavaScript code into single file
```bash
ncc build index.js -o action
```

- Create `git_update.sh`
- Make `git_update.sh` executable
```bash
chmod +x chmod +x action/git_update.sh
```

- Commit and push
```bash
git add .
git commit -m 'init commit'
git tag -a -m "increment git tag" v1
git push --follow-tags
```

## Test JavaScript GitHub Action

- Create GitHub repository `lesson-088` (private)

- Clone repo
```bash
git clone git@github.com:antonputra/lesson-088.git
```

- Create `.github/workflows/main.yaml` (patch)

- Commit and push

- Increment major version, commit and push

## Links

- [Creating a JavaScript action](https://docs.github.com/en/actions/creating-actions/creating-a-javascript-action)
- [@actions/core](https://github.com/actions/toolkit/tree/master/packages/core)
- [@actions/exec](https://github.com/actions/toolkit/tree/master/packages/exec)
