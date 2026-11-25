#!/usr/bin/env bash
# One-time publish: repo, 3 issues, 3 merged feature-branch PRs, wait for CI, write measured numbers into README.
# Needs git + gh (run `gh auth login` once).
set -euo pipefail
REPO=hamza2829/qa-automation-lab
export GIT_AUTHOR_NAME="Hamza Sohail" GIT_AUTHOR_EMAIL="hamzashiekh2829@gmail.com"
export GIT_COMMITTER_NAME="$GIT_AUTHOR_NAME" GIT_COMMITTER_EMAIL="$GIT_AUTHOR_EMAIL"
F1="tests/e2e"; F2="scripts/derive_test_cases.py data/requirements.csv"; F3="scripts/bug_matrix.py docs/bugs"
mkdir -p ../_stash && for p in $F1 $F2 $F3; do mkdir -p "../_stash/$(dirname $p)"; mv "$p" "../_stash/$p"; done
git init -b main && git add -A && git commit -m "Shop app, API tests, Groovy checks, runner, CI and Jenkinsfile"
gh repo create "$REPO" --public --source=. --push
num() { grep -o '[0-9]*$'; }
I1=$(gh issue create -R $REPO -t "Playwright E2E tests with page objects" -b "Login, cart, checkout; screenshots on failure." | num)
I2=$(gh issue create -R $REPO -t "Derive test cases from requirements CSV" -b "Requirement IDs, scope, test case list." | num)
I3=$(gh issue create -R $REPO -t "Bug detection matrix" -b "Start app per seeded bug and prove one test fails per bug." | num)
pr() { local b=$1 i=$2 t=$3; shift 3
  git checkout -b "$b" main
  for p in "$@"; do mkdir -p "$(dirname $p)"; mv "../_stash/$p" "$p"; done
  git add -A && git commit -m "$t (closes #$i)" && git push -u origin "$b"
  gh pr create -R $REPO -B main -H "$b" -t "$t" -b "Closes #$i"
  gh pr merge "$b" -R $REPO --merge --delete-branch
  git checkout main && git pull --ff-only origin main; }
pr feature/e2e "$I1" "Add Playwright E2E tests" $F1
pr feature/requirements "$I2" "Derive test cases from requirements" $F2
pr feature/bug-matrix "$I3" "Add bug detection matrix and bug reports" $F3
rm -rf ../_stash
sleep 15
RUN=$(gh run list -R $REPO -b main -L1 --json databaseId -q '.[0].databaseId')
gh run watch -R $REPO --exit-status "$RUN" | tail -n 20
# Verify from a fresh clone and use only measured numbers
TMP=$(mktemp -d); gh repo clone $REPO "$TMP/repo"; cd "$TMP/repo"
gh run download "$RUN" -R $REPO -n test-reports -D ci
python3 scripts/update_readme.py ci/reports
git commit -am "README: measured CI results" && git push origin main
