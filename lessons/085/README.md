# How to Deploy React App on Firebase Hosting? (CI/CD with GitHub Actions | Preview | Custom Domain)

[YouTube Tutorial](https://youtu.be/Bnd4IO3f2hU)

## Prerequisites

- Firebase Account
- npm 5.2+

## Create React App from Scratch 2021

- Check `npm` version

```bash
npm --version
```

- Create a new single-page application in React

```bash
npx create-react-app react-demo-085
```

- Change directory to the app

```bash
cd react-demo-085
```

- Inspect the folder content

```bash
code .
```

- Run react locally

```bash
npm start
```

## Create Firebase Project

- Go to [Firebase](https://firebase.google.com/)

- Click `Go to console`

- Click `Create a project`

- Create `react-demo-085` Firebase project

## Deploy React App on Firebase Hosting

- Install the Firebase CLI

```bash
npm install -g firebase-tools
```

- Log in and test the Firebase CLI

```bash
firebase login
```

- Test that the CLI is properly installed and accessing your account by listing your Firebase projects.

```bash
firebase projects:list
```

- Build for React application

```bash
npm run build
```

- Initialize your project

```bash
firebase init hosting
```

- Deploy to your site

```bash
firebase deploy --only hosting
```

- Open hosting URL

- Check TLS certificate

## Firebase Hosting Add Custom Domain

- Go to Firebase console

- Navigate to `Hosting`

- Click `Add custom domain`

- Enter your domain, in my case `devopsbyexample.io`

- Create A record for your domain

- Optionally add `www` subdomain

## Set up automatic builds and deploys with GitHub

- Create GitHub repo `react-demo-085`, let's make it private

- Add existing repository

```bash
git remote add origin git@github.com:antonputra/react-demo-085.git
git add .
git commit - 'init commit'
git push origin main
```

- Reinitialize Firebase hosting

```bash
firebase init hosting
```

- Create new branch for new feature

```bash
git checkout -b feature-x
```

- Modify `src/App.js`

- Commit, push and create PR

```bash
git add .
git commit -m 'Add new feature X'
git push origin feature-x
```

- Go to `Actions` in GitHub repo

## Links

- [Get started with Firebase Hosting](https://firebase.google.com/docs/hosting/quickstart)
- [npx: an npm package runner](https://medium.com/@maybekatz/introducing-npx-an-npm-package-runner-55f7d4bd282b)
- [Firebase Pricing](https://firebase.google.com/pricing?authuser=0)

## Clean Up

- Remove `react-demo-085` firebase project

- Remove `firebase-tools`

```bash
npm uninstall -g firebase-tools
```

- Remove `react-demo-085` GitHub repo

- Remove DNS records

- Log out from Firebase

```bash
firebase logout
```
