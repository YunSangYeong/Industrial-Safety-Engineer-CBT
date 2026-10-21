# 검증 보고서

작업일: 2026-10-21 (Asia/Seoul). 대상 저장소: YunSangYeong/Industrial-Safety-Engineer-CBT.
기준 앱: YunSangYeong/electrician-cbt `b9a682ccff1b460334b78d5bfad9375b7ec4fbb6`. 스킬: v1.3.1.

## 근거

- Q-Net 상세정보와 취득방법 응답을 읽어 6과목·20문항/과목·30분/과목·4지선다·40점 과락·평균60점을 확인했다. 초기 403 후 네트워크 변경 상태에서 정상 재조회했다. `official-rules-evidence.json`에 확인 문구와 원문 해시를 보관한다.
- 앱 기준 커밋에서 App/model/styles·패키지·lockfile·설정·테스트를 재사용했다. 문제 데이터는 재사용하지 않았다. 기존 AGENTS.md 부재를 확인 후 연결 파일을 만들었다.
- Node 24.19.0/npm 11.9.0. 서명·체크섬·TLS 검증 해제 없음. 첫 설치는 쓰기 불가 기본 npm cache 때문에 실패했다. 쓰기 가능한 `/tmp/industrial-cbt-npm-cache`로 변경해 동일 lockfile로 npm ci 성공했다.

## 로컬 검증

작업 디렉터리는 `/workspace/Industrial-Safety-Engineer-CBT`다.

- `npm run check`: 단위·문항 테스트 892개 통과, TypeScript 및 프로덕션 빌드 성공 (exit 0).
- `PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH=/usr/bin/chromium npm run test:e2e`: 총 28개 중 27개 통과·1개 해당 없음(데스크톱의 모바일 터치 전용 검사), exit 0. 1차 재사용 테스트의 검수 문구 기대 문자열 오류 2건은 실제 문구로 수정했다. 앱 기능 오류를 숨기기 위해 검증을 제거하지 않았다.
- Chromium 데스크톱과 Pixel 7 에뮬레이션. 120문항 중 과목별12개 정답으로 평균60·모든 과목 과락 없음, 결과120개·오답48개, 복원·자동제출·미응답·북마크·통계·등록·로컬 승인·CSV·초기화·손상 원본 보존을 확인한다.
- 두 모드 실제 Space keydown/keyup·포커스·미응답/마지막/수정키/길게 누르기/컨트롤/대화상자 경계를 확인한다.
- 390×480 및 740×360에서 실제 휠 아래/위 이동, 하단 백업·초기화·상단 대시보드 접근. 별도 모바일 CDP touchStart/move/end 스와이프와 글자 확대·뷰포트 높이 변경을 확인한다. scrollTop 값을 강제 변경해 통과시키지 않는다.
- 동일 origin iframe 내부 Space·저장 분리·백업 다운로드를 검사한다. 실제 외부 블로그의 제3자 저장 정책은 미실행이다.
- `python3 scripts/generate_bank.py` 전후 JSON·양식 해시가 일치함을 확인한다. 1,000개 ID·정규화 fingerprint 고유성, 계산880개 별도 수식·단위·정답 검증. 생성기와 검증기 구현 언어/수식 경로를 분리했다.
- PC·모바일 스크린샷으로 실제 레이아웃을 확인했다. 학습 기준 선택·상시 상단 면책 배너 부재와 저장 실패 경고를 확인한다.

실기기·Safari·Firefox는 미실행. 전문가 검수와 문항별 공식 세부 출제기준 대조는 미완료. 기본 은행1,000개는 내부 검수 완료 의미이며 전문가 검수1,000개라고 주장하지 않는다. 프로덕션 문제 청크 크기 경고는 존재하며 브라우저 기능 테스트는 통과한다.

## CI와 공개 배포

push/PR는 검증만 수행하고 배포 job은 main의 workflow_dispatch에서만 실행한다. 사용자 이번 요청이 실제 배포를 명시하여 에이전트 실행을 위임했다. 기본 스킬의 향후 사용자 수동 배포 정책은 그대로 보존한다. 정확한 실행 커밋·CI·공개 사이트 결과는 실행 후 기록한다.
