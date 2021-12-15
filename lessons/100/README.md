# How to Deploy Create React App to GitHub Pages?

[YouTube Tutorial](https://youtu.be/K5DTIf-jWhk)

## Create React App & GitHub Repo

- Create `react-pages-demo` empty GitHub repository

- Create react app using `create-react-app` tool

```bash
npx create-react-app react-pages-demo
```

- Test react app locally

```bash
cd react-pages-demo
npm start
```

## Deploy React App to GitHub Pages

- Add `homepage` attribute to the `package.json` file

```json
{
    ...
    "homepage": "https://antonputra.github.io/react-pages-demo",
    ...
}
```

- Install `gh-pages` npm module to publishing files to a gh-pages branch on GitHub

```bash
npm install gh-pages
```

- Add couple of tasks to `package.json` file

```json
{
    ...
    "scripts":
    {
        ...
        "predeploy": "npm run build",
        "deploy": "gh-pages -d build"
    }
}
```

- Connect local repository to the remote

```bash
git remote add origin git@github.com:antonputra/react-pages-demo.git
git branch -M main
git push -u origin main
```

- Deploy react app to GitHub pahes

```bash
npm run deploy
```

## Setup Custom Domain for GitHub Pages

- Set your custom DNS name from the GitHub settings Pages (devopsbyexample.io)

- Go to your DNS provider (in my case Google Domains)

- Create `A` record for your Apex domain (devopsbyexample.io)

```bash
185.199.108.153
185.199.109.153
185.199.110.153
185.199.111.153
```

- Create `CNAME` record for `www` subdomain
  - www -> antonputra.github.io
  
- Add `CNAME` file under `public` directory

```
devopsbyexample.io
```

- Update homepage attribute

```json
{
    ...
    "homepage": "https://devopsbyexample.io",
    ...
}
```

- Commit the changes and deploy to github pages

```bash
git add .
git commit -m 'Add custom domain'
git push origin main
npm run deploy
```

## Automate Deployment with GitHub Actions

- Create `.github/workflows/github-pages.yml` GitHub actions workflow

```yaml
---
name: Build and Deploy React App to GitHub Pages
on:
  push:
    branches: [ main ]
jobs:
  build-and-deploy:
    name: Build and Deploy
    runs-on: ubuntu-latest

    steps:
    - name: Checkout
      uses: actions/checkout@v2

    - name: Build
      run: npm install

    - name: Test
      run: npm run test

    - name: Deploy
      run: |
        git config --global user.name 'Anton Putra'
        git config --global user.email 'me@antonputra.com'
        git remote set-url origin https://x-access-token:${{ secrets.GITHUB_TOKEN }}@github.com/${{ github.repository }}    
        npm run deploy
```

- Update `src/App.js` with random text

- Commit and push

```bash
git add .
git commit -m 'Add GitHub Actions'
git push origin main
```

## Links

- [GitHub gh-pages](https://github.com/tschaub/gh-pages)
