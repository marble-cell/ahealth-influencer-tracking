# 인플루언서 가입 트래킹

인플루언서별 초대 코드 가입·링크 가입 수와 업로드 날짜를 보여 주는 아티팩트.

## 파일
- `index.html`: build.py 가 만드는 페이지(레포에는 안 올림). claude.ai 아티팩트는 이 파일을 같은 경로로 다시 게시한다.
- `data/data.json`: 기준 시각, 인플루언서(코드·링크·추적용 계정 회원 ID·업로드 날짜), 가입 기록.
- `build.py`: data.json → index.html. `python3 build.py`
- `template.css`: 방정식 페이지와 같은 디자인.

## 숫자 갱신
0. 가입 합계는 Mixpanel(project 3046325) `invite-regist-complete` 순 사용자를 `invite_code` 로 나눠 data.json 의 `mixpanel.by_code` 에 넣는다(11/15부터, 커스텀 그룹으로 인플루언서 코드만). 몽고 인증이 없어도 된다.
MongoDB MCP Prod, `tracer` DB.
1. `users` 를 `inviter_id` ∈ 추적용 계정 회원 ID 로 조회(`inviter_id_1` 인덱스) → 가입자와 `created_at`, `device_os`.
2. `points` 를 `invitee_id` ∈ 가입자 ID 로 조회(`invitee_id_1` 인덱스) → `event: INFLUENCER_INVITEE`.
   `event_meta` 가 `random-point-referral` 이면 링크 가입, 없으면 초대 코드 가입.
3. 업로드 날짜는 Notion '인플루언서 일정' DB(collection://f0fc35c0-74e1-4e25-9e00-f81c52d62e99)의 종류=업로드 행.
4. data.json 을 고치고(시각은 한국 시간) build.py 를 돌린 뒤 commit·push 한다. GitHub Actions 가 Pages 를 다시 게시한다.

## 비용·반응 갱신
- 게시물 지표: `node tools/clips.mjs <인스타 계정>` (HikerAPI) → 조회·좋아요·댓글·공유·저장을 data.json 에 옮긴다.
- 비용: Notion '인플루언서 섭외' 페이지의 합의 금액, 지스터는 일정 DB 의 85만.
- 한국 광고 평균(`kr_paid`): Notion '인플루언서 섭외' 페이지의 Paid 광고 매체별 단가(10/06~11/05) + 같은 기간 `users` 한국 신규 가입 수(`created_at` 범위, `device_country: KR`).

## 누구나 갱신하기
레포: https://github.com/marble-cell/ahealth-influencer-tracking (공개)
페이지: https://marble-cell.github.io/ahealth-influencer-tracking/ (링크 있는 누구나 열람)
수정하려면 marble-cell 이 레포 collaborator 로 추가해 줘야 한다.
1. `git clone` 또는 `git pull --rebase`
2. `data/data.json` 수정 → `python3 build.py` 로 확인
3. commit·push → GitHub Actions 가 GitHub Pages 를 다시 게시한다.
Claude 에게 맡길 때는 이 레포 폴더에서 "인플루언서 가입 트래킹 갱신해"라고 하면 CLAUDE.md 순서를 따른다.
