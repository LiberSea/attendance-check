# 대학교 출석체크 시스템 (Attendance Check)

Django 기반 대학교 출석체크 시스템입니다.

## 주요 기능
- 회원가입/로그인/로그아웃, 비밀번호 찾기 (학생·교수 역할 구분)
- 강의 개설 및 강의 코드 기반 수강신청
- 출석 코드/QR코드 기반 학생 체크인
- 세션 자동 마감 시간 및 지각 자동 판정
- 출석 통계(출석률) 조회 및 CSV 내보내기
- Django 관리자 페이지

## 기술 스택
- Python / Django
- SQLite (로컬 개발) / PostgreSQL (Docker 배포)

## 로컬 개발 환경 실행

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## Docker로 실행하기

1. 환경변수 파일을 준비합니다.

   ```bash
   cp .env.example .env
   # .env 파일을 열어 DJANGO_SECRET_KEY, POSTGRES_PASSWORD 등을 실제 값으로 변경하세요.
   ```

2. 빌드 후 실행합니다.

   ```bash
   docker compose up -d --build
   ```

   최초 실행 시 PostgreSQL 컨테이너가 준비된 후 `web` 컨테이너가 자동으로
   마이그레이션과 정적 파일 수집(`collectstatic`)을 수행하고 gunicorn으로
   서비스를 기동합니다.

3. http://localhost:8000 으로 접속합니다.

4. 관리자 계정이 필요하면 컨테이너 안에서 생성합니다.

   ```bash
   docker compose exec web python manage.py createsuperuser
   ```

5. 종료하려면:

   ```bash
   docker compose down
   ```

## 개발 브랜치 전략
- 각 작업 단계는 이전 단계 브랜치를 기반으로 새 브랜치를 만들어 진행합니다.
- 전체 작업이 완료되면 각 브랜치를 `main`으로 merge 후 GitHub에 push합니다.
