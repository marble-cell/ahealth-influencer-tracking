// 업로드된 릴스의 조회·좋아요·댓글·공유·저장 수를 HikerAPI 로 가져온다. node clips.mjs <계정> [<계정>...]
// pulse-marketing plugin 의 hiker.mjs 를 쓴다. 어느 계정·컴퓨터에서든 설치된 가장 최근 버전을 찾는다.
import {readdirSync, statSync, writeFileSync} from 'node:fs';
import {homedir} from 'node:os';
import {join} from 'node:path';
import {pathToFileURL} from 'node:url';
const base = join(homedir(), '.claude/plugins/cache/grvtlabs-pulse/pulse-marketing');
const hiker = readdirSync(base).map(v => join(base, v, 'skills/ahealth-influencer-search/scripts/hiker.mjs'))
  .filter(p => { try { return statSync(p).isFile(); } catch { return false; } })
  .sort((a, b) => statSync(b).mtimeMs - statSync(a).mtimeMs)[0];
if (!hiker) throw new Error('pulse-marketing plugin 의 hiker.mjs 가 없습니다. pulse-marketing 을 설치하세요.');
const {makeClient} = await import(pathToFileURL(hiker).href);
const get=makeClient();
for(const u of process.argv.slice(2)){
  const p=await get('/v1/user/by/username',{username:u});
  const d=await get('/v2/user/clips',{user_id:p.pk});
  writeFileSync(new URL(`../data/clips_${u}.json`, import.meta.url),JSON.stringify(d));
  const items=(d.response?.items||[]).map(x=>x.media||x);
  for(const m of items.slice(0,6)){
    console.log(u,m.code,new Date(m.taken_at*1000+9*3600000).toISOString().slice(0,16),'play',m.play_count,'ig_play',m.ig_play_count,'like',m.like_count,'cmt',m.comment_count,'share',m.reshare_count,'save',m.save_count,'| coauth',(m.coauthor_producers||[]).map(c=>c.username).join(','),'|',(m.caption?.text||'').replace(/\s+/g,' ').slice(0,70));
  }
}
