#!/bin/bash
GH_REPO="@github.com/mkdocs/mkdocs.git"
FULL_REPO="https://${GH_TOKEN}$GH_REPO"
GH_NAME="mkdocs";
GH_EMAIL="travis@mkdocs.org"

mkdir -p out
cd out

git init
git remote add origin $FULL_REPO
git fetch
git config user.name $GH_NAME
git config user.email $GH_EMAIL
git checkout gh-pages

cd ../

mkdocs build --clean -d out

cd out

touch .
git add -A .
git commit -m "GH-Pages update by travis after $TRAVIS_COMMIT"
git push -q origin gh-pages
