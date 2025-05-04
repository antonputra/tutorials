# Git Submodules Explained: Tutorial | Example | Guide | GitHub | Add | Update

[YouTube Tutorial](https://youtu.be/wTGIDDg0tK8)

## Create Two Repos

```bash
# create module-a with README
# create module-b with README
git clone git@github.com:antonputra/module-a.git
cd module-a
git submodule add git@github.com:antonputra/module-b.git
git status
git diff --cached --submodule
git commit -am 'Add module-b'
git push origin main
```

## Cloning a Project with Submodules
```bash
cd ..
rm -rf module-a
git clone git@github.com:antonputra/module-a.git
cd module-a
code .
git submodule update --init --recursive
cd ..
rm -rf module-a
Optionally: git clone --recurse-submodules git@github.com:antonputra/module-a.git
cd module-a
code .
```

## Pulling in Upstream Changes from the Submodule Remote
```bash
# Add "update v2" to README.md in module-b and commit "Update README.md v2"
cd module-b
git fetch
git merge origin/main
cd ..
git diff
git diff --submodule
git config --global diff.submodule log
git diff
# Optionally: easier way
# Make another change in module-b "Update README.md v3"
git submodule update --remote
git status
git config status.submodulesummary 1
git status
git commit -am 'Update Submodule'
git push origin main
```

## Working on a Submodule
```bash
code .
cd module-b
git checkout main
git pull
# add main.py print('Hello')
git add main.py
git commit -m 'Add main.py'
cd ..
git submodule update --remote --merge
# (make change in module-b "Update README.md v4")
git submodule update --remote --rebase
git commit -am 'Update Submodule'
```

## Publishing Submodule Changes
```bash
git diff
git push --recurse-submodules=check
git config push.recurseSubmodules check
git push
git push --recurse-submodules=on-demand
```