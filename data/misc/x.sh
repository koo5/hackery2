#!/bin/bash -e
rm -rf example
git init example
cd example
cat > file.txt << EOF
0
0
0
0
0
0
0
0
0
0
0
0
EOF
git add file.txt
git commit -am "initial"
git branch branch1
git branch branch2
git branch branch3
cat > file.txt << EOF
master
0
0
0
0
0
0
0
0
0
0
0
EOF
sleep 1
git commit -am "commit directly on master"
git checkout branch1
cat > file.txt << EOF
0
0
0
branch1
0
0
0
0
0
0
0
0
EOF
sleep 1
git commit -am "branch 1"


git checkout branch2
cat > file.txt << EOF
0
0
0
0
0
0
branch2
0
0
0
0
0
EOF
sleep 1
git commit -am "branch 2"

git checkout master
sleep 1
git merge --no-edit branch2

git checkout branch3
cat > file.txt << EOF
0
0
0
0
0
0
0
0
0
0
0
branch3
EOF
sleep 1
git commit -am "branch 3"

git checkout master
sleep 1
git merge --no-edit branch1
sleep 1
git merge --no-edit branch3
echo
git log --pretty="format:%h %ar %s"
echo
git log --pretty="format:%h %ar %s" --graph
echo
git log --pretty="format:%h %ar %s" --first-parent
