# M2-T03-2026-06-18-001-PostgreSQL-스키마-불일치-API-오류-수정

Status: Done
Created: 2026-06-18
Updated: 2026-06-18
Owner: Codex

## 목표

기존 PostgreSQL 개발 DB에 M2 신규 테이블이 없는 상태에서 API 서버가 `/v1/dashboard/summary` 요청을 500으로 응답하는 문제를 수정한다.

## 요구사항 링크

- Product source of truth: `docs/01_Product.md`
- Architecture source of truth: `docs/02_Architecture.md`
- DB contract: `docs/contracts/db/schema.sql`
- Verification evidence: `docs/Test/2026-06-18-PostgreSQL-스키마-불일치-API-오류-검증.md`

## 우선순위

P0

## 선행 Task

- `docs/Task/M2-T01-2026-06-18-001-데이터-수집관리-화면-재설계와-수집계획-계약.md`

## 범위

- 포함: PostgreSQL 저장소 초기화 시 기존 DB에도 누락된 schema를 보강
- 포함: DB 계약을 반복 적용 가능한 idempotent DDL(Data Definition Language)로 정리
- 포함: 기존 DB에 `collection_plans`, `collection_coverage_snapshots`, `collection_coverage_segments`가 없을 때의 회귀 테스트
- 포함: 실제 개발 DB에서 API 재시작 후 `/v1/dashboard/summary` 200 응답 확인
- 포함: API 재시작 검증 중 발견한 `dev.sh` 장기 실행 Python 프로세스 실행 방식 보강

## 비범위

- 운영용 migration 프레임워크 도입
- 기존 테이블 컬럼 변경이나 데이터 변환 migration
- PostgreSQL 볼륨 삭제 또는 초기화

## 현재 맥락

M2 화면 계약에서 `collection_plans`, `collection_coverage_snapshots`, `collection_coverage_segments`가 추가됐다. 그러나 기존 개발 DB는 M1 schema로 만들어져 `instruments`는 존재하지만 신규 M2 테이블은 없다. 기존 `PostgresOperationsRepository`는 `instruments` 존재 여부만 확인하고 schema 적용을 건너뛰어 API가 신규 테이블 조회 시 실패했다.

## 설계 메모

- 개발 환경에서는 DB 볼륨을 유지하면서 앱 코드만 재시작할 수 있어야 한다.
- 따라서 `schema.sql`은 반복 적용해도 실패하지 않는 `CREATE TABLE IF NOT EXISTS`, `CREATE INDEX IF NOT EXISTS` 형태로 유지한다.
- 저장소 초기화는 비어 있는 DB인지 여부와 관계없이 schema 계약을 적용한다.
- `dev.sh`는 API와 worker 같은 장기 실행 Python 프로세스를 `uv run` wrapper가 아니라 `.venv/bin/python`으로 직접 실행한다.
- 기존 테이블의 구조 변경처럼 `IF NOT EXISTS`로 해결되지 않는 변경은 별도 migration Task로 분리한다.

## 계약 링크

- `docs/contracts/db/schema.sql`

## 계약 변경

- 모든 `CREATE TABLE` 문을 `CREATE TABLE IF NOT EXISTS`로 변경
- 모든 `CREATE INDEX` 문을 `CREATE INDEX IF NOT EXISTS`로 변경
- `docs/contracts/db/README.md`에 idempotent DDL 적용 기준 추가

## 실패 케이스

- 기존 DB에 `instruments`만 있고 `collection_plans`가 없을 때 API `/v1/dashboard/summary`가 500으로 실패함
- `schema.sql`을 재적용할 때 기존 테이블 또는 인덱스 때문에 duplicate 오류가 발생함
- 저장소 초기화가 기존 DB라는 이유로 schema 적용을 건너뜀

## 실행 계획

- [x] Step 1: 첨부 로그와 실제 API 응답으로 오류를 재현한다.
- [x] Step 2: DB 계약이 idempotent DDL이어야 한다는 실패 테스트를 추가한다.
- [x] Step 3: PostgreSQL 저장소가 기존 테이블 존재 시에도 schema를 적용해야 한다는 실패 테스트를 추가한다.
- [x] Step 4: `schema.sql`과 `PostgresOperationsRepository`를 수정한다.
- [x] Step 5: 실제 개발 DB에서 API를 재시작하고 `/v1/dashboard/summary` 200 응답을 확인한다.
- [x] Step 6: API 재시작 안정화를 위해 `dev.sh`의 Python 장기 프로세스 실행 방식을 보강한다.
- [x] Step 7: 자동화 검증과 문서 증적을 완료한다.
- [x] Step 8: 기능 단위 한글 커밋을 생성한다.

## 완료 기준

- 기존 개발 DB에서 `collection_plans`, `collection_coverage_snapshots`, `collection_coverage_segments`가 생성된다.
- `/v1/dashboard/summary`가 500 대신 200으로 응답한다.
- 회귀 테스트가 스키마 불일치를 포착한다.
- 전체 테스트, 린트(Lint), 타입 검사(Type Check), 빌드, E2E(End-to-End)가 통과한다.

## 검증

```bash
uv run pytest tests/contracts/test_db_contract.py tests/shared/test_postgres_repository_schema.py -q
uv run pytest -q
uv run ruff check .
uv run mypy apps packages tests
npm test
npm run build
npm run e2e
git diff --check
```

## 실행 로그

- 2026-06-18: 첨부 로그에서 `psycopg.errors.UndefinedTable: relation "collection_plans" does not exist` 확인.
- 2026-06-18: 실제 개발 DB에서 `instruments`는 존재하고 `collection_plans`, `collection_coverage_snapshots`, `collection_coverage_segments`는 없음을 확인.
- 2026-06-18: 실패 테스트를 추가해 schema idempotency와 저장소 schema 적용 누락을 재현.
- 2026-06-18: API 재시작 후 실제 개발 DB에 신규 테이블 3개가 생성되고 `/v1/dashboard/summary`가 200으로 응답함을 확인.
- 2026-06-18: `dev.sh app start api`가 `uv run` wrapper PID를 기록한 뒤 리스너가 사라지는 문제를 확인하고 `.venv/bin/python -m uvicorn` 실행으로 보강.

## 복잡도 제한

- migration 프레임워크를 도입하지 않는다.
- 기존 schema.sql을 단일 DB 계약 기준으로 유지한다.
- 기존 개발 DB를 삭제하지 않는다.

## 추적성

- 제품 요구사항: GM-PROD-022
- 관련 화면: 데이터 수집관리 > 운영 상태 대시보드
- 관련 계약: `DashboardSummary.targets`, `collection_plans`, `collection_coverage_snapshots`, `collection_coverage_segments`
