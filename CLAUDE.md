# 인플루언서 가입 트래킹 — Claude 작업 규칙

이 레포가 기준이다. 어느 Claude 계정·어느 컴퓨터에서 작업하든 아래 순서를 따른다.

1. 시작 전에 `git pull --rebase` 로 최신을 받는다. 다른 사람이 먼저 고쳤을 수 있다.
2. 숫자는 `data/data.json` 만 고친다. 갱신 방법(MongoDB·Notion·HikerAPI)은 README.md 에 있다.
3. `python3 build.py` 가 오류 없이 도는지 확인한다.
4. `git add -A && git commit -m "기록 갱신 MM/DD HH:MM" && git push`.
   push 하면 GitHub Actions 가 페이지를 다시 만들어 GitHub Pages 에 올린다(1~2분).
5. claude.ai 아티팩트(https://claude.ai/artifact/An4x1e7FE6wR2N41zs66F4)는 만든 사람 계정에서만 다시 게시할 수 있다.
   그 계정이면 `index.html` 을 같은 url 로 다시 게시하고(먼저 Artifact read), 아니면 건너뛴다. 공유 링크는 GitHub Pages 주소(https://marble-cell.github.io/ahealth-influencer-tracking/)다.

push 가 거절되면 `git pull --rebase` 뒤 data.json 충돌을 직접 합치고 다시 build 한다. 남의 갱신을 덮어쓰지 않는다.
