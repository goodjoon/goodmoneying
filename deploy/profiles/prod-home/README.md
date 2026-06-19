# prod-home 배포 프로필

`prod-home`은 운영계(prod)를 홈 인프라(home)에 배포하는 프로필이다.

## 서버 역할

| 서버 | 역할 | 서비스 |
|---|---|---|
| Mac Mini M4 | infra, 배포 제어 | postgres, GitHub Actions runner |
| APP SERVER 01 | application | api, worker |
| bmax-ubuntu | web | web |

## 비밀값

비밀값은 repo에 커밋하지 않는다. 각 서버의 `/opt/goodmoneying/env/` 아래에 둔다.

- `/opt/goodmoneying/env/infra.env`
- `/opt/goodmoneying/env/app.env`
- `/opt/goodmoneying/env/web.env`
- `/opt/goodmoneying/env/ghcr.env`

## 서버별 env 파일

아래 값은 형식 예시다. 실제 운영 값은 별도로 생성하고 배포 전 회전(rotate)한다.

### Mac Mini M4: `/opt/goodmoneying/env/infra.env`

```bash
POSTGRES_DB=goodmoneying
POSTGRES_USER=goodmoneying
POSTGRES_PASSWORD=prod-home-example-postgres-password-rotate
```

### APP SERVER 01: `/opt/goodmoneying/env/app.env`

```bash
GOODMONEYING_DATABASE_URL=postgresql://goodmoneying:prod-home-example-postgres-password-rotate@Mac-Mini-M4.local:5432/goodmoneying
GOODMONEYING_OPERATOR_TOKEN=prod-home-example-operator-token-rotate
GOODMONEYING_LIVE_UPBIT=1
```

### bmax-ubuntu: `/opt/goodmoneying/env/web.env`

```bash
GOODMONEYING_WEB_INTERNAL_URL=http://bmax-ubuntu:8080
```

Web 정적 앱의 API base URL은 런타임 env가 아니라 Docker build arg로 이미지에 반영된다. `deploy.yml`은 운영 web 이미지 빌드 시 `VITE_API_BASE_URL=http://app-server01:8000`을 주입한다.

## GHCR pull 로그인

각 운영 서버에서 private GHCR(GitHub Container Registry) 이미지를 pull하려면 read-only 권한 토큰을 사용해 로그인한다.

```bash
printf '%s' "$CR_PAT" | docker login ghcr.io -u goodjoon-company --password-stdin
```

모든 서버는 Tailscale 내부 hostname으로 서로 접근 가능해야 한다.

## 수동 dry-run

```bash
GOODMONEYING_DEPLOY_DRY_RUN=1 deploy/scripts/deploy-profile.sh prod-home release-abc1234
```
