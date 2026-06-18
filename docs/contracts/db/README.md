# DB 계약

DB schema의 source of truth를 둔다.

## 기준 파일

- `schema.sql`: 현재 기준 PostgreSQL schema
- migration 파일 또는 migration 디렉터리 링크: 실제 적용 순서가 중요한 경우

## 기록 기준

- 테이블, 컬럼, 제약조건, 인덱스, view, trigger 등 DB가 강제하는 정의를 기록한다.
- Architecture 문서에는 schema 상세를 복사하지 않고 이 위치를 링크한다.

## 적용 기준

- `schema.sql`은 개발 환경에서 반복 적용해도 실패하지 않는 idempotent DDL(Data Definition Language)로 유지한다.
- 운영 서버(Operations Server)는 시작 시 `schema.sql`을 적용해 기존 개발 DB에 새 테이블 또는 인덱스가 추가된 경우에도 누락 schema를 보강한다.
- 기존 테이블의 컬럼 변경, 제약조건 변경, 데이터 변환이 필요한 경우에는 별도 migration 작업과 검증 증적을 추가한다.
