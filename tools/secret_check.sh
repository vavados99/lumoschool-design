#!/usr/bin/env bash
# Проверка перед коммитом: нет ли секретов в хранилище и в подготовленных изменениях.
# Значения ключей не печатает. Запуск из папки хранилища ПОСЛЕ git add:
#   bash /root/projects/english-school/tools/secret_check.sh
# Код выхода 0 — чисто, 1 — найдено (не коммитить).
set -u
ENV_FILE="${ENV_FILE:-/root/.hermes/.env}"
fail=0
bad_files=$(git ls-files --cached | grep -E '(^|/)\.env($|\.)|\.(db|sqlite|pem|key)$|(^|/)id_(rsa|ed25519)' | grep -v '\.env\.example$')
if [ -n "$bad_files" ]; then echo "НАЙДЕНО: секретные файлы в хранилище:"; echo "$bad_files"; fail=1; fi
if git diff --cached -U0 | grep -E '^\+' | grep -qE '(^|[^A-Za-z0-9])sk-(ant-)?[A-Za-z0-9_-]{20,}|ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|-----BEGIN [A-Z ]*PRIVATE KEY|AKIA[0-9A-Z]{16}|xox[abp]-[A-Za-z0-9-]{10,}'; then
  echo "НАЙДЕНО: похоже на ключ в подготовленных изменениях"; fail=1; fi
if [ -r "$ENV_FILE" ]; then
  vals=$(sed -E 's/^[[:space:]]*export[[:space:]]+//' "$ENV_FILE" | awk '!/^[[:space:]]*#/ && index($0,"=")>0 { v=substr($0,index($0,"=")+1); gsub(/^["\047]|["\047][[:space:]]*$/,"",v); if (length(v)>=16) print v }')
  if [ -z "$vals" ]; then
    echo "НАЙДЕНО: в $ENV_FILE нет значений для сверки, проверка невозможна"; fail=1
  elif git diff --cached | grep -qF -f <(printf '%s\n' "$vals"); then
    echo "НАЙДЕНО: значение из .env в подготовленных изменениях"; fail=1; fi
else
  echo "НАЙДЕНО: не могу прочитать $ENV_FILE, сверка невозможна"; fail=1
fi
[ "$fail" -eq 0 ] && echo "секретов нет"
exit "$fail"
