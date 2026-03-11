flowcrm/
├── README.md
├── .gitignore
├── .editorconfig
├── .env.example
├── docker-compose.yml
├── docs/
│   ├── prd/
│   │   └── FlowCRM-PRD.docx
│   ├── planning/
│   │   ├── sprints.md
│   │   ├── architecture.md
│   │   ├── api-contracts.md
│   │   └── decisions.md
│   ├── diagrams/
│   │   ├── erd.png
│   │   ├── backend-architecture.png
│   │   └── frontend-routing.png
│   └── api/
│       └── openapi.yaml
├── backend/
│   ├── manage.py
│   ├── requirements/
│   │   ├── base.txt
│   │   ├── dev.txt
│   │   └── prod.txt
│   ├── config/
│   │   ├── __init__.py
│   │   ├── asgi.py
│   │   ├── wsgi.py
│   │   ├── urls.py
│   │   └── settings/
│   │       ├── __init__.py
│   │       ├── base.py
│   │       ├── dev.py
│   │       ├── prod.py
│   │       └── test.py
│   ├── apps/
│   │   ├── common/
│   │   │   ├── models.py
│   │   │   ├── permissions.py
│   │   │   ├── pagination.py
│   │   │   ├── mixins.py
│   │   │   └── utils.py
│   │   ├── accounts/
│   │   │   ├── models.py
│   │   │   ├── serializers.py
│   │   │   ├── views.py
│   │   │   ├── urls.py
│   │   │   ├── services.py
│   │   │   ├── selectors.py
│   │   │   └── tests/
│   │   ├── organizations/
│   │   ├── leads/
│   │   ├── deals/
│   │   ├── activities/
│   │   ├── tasks/
│   │   └── analytics/
│   ├── scripts/
│   │   ├── seed_demo_data.py
│   │   └── wait_for_db.py
│   ├── static/
│   ├── media/
│   ├── pytest.ini
│   └── Dockerfile
├── frontend/
│   ├── package.json
│   ├── tsconfig.json
│   ├── next.config.ts
│   ├── postcss.config.js
│   ├── tailwind.config.ts
│   ├── public/
│   ├── src/
│   │   ├── app/
│   │   │   ├── (auth)/
│   │   │   │   ├── login/page.tsx
│   │   │   │   └── register/page.tsx
│   │   │   ├── (dashboard)/
│   │   │   │   ├── dashboard/page.tsx
│   │   │   │   ├── leads/
│   │   │   │   │   ├── page.tsx
│   │   │   │   │   └── [id]/page.tsx
│   │   │   │   ├── deals/
│   │   │   │   │   ├── page.tsx
│   │   │   │   │   └── [id]/page.tsx
│   │   │   │   ├── pipeline/page.tsx
│   │   │   │   ├── tasks/page.tsx
│   │   │   │   └── settings/
│   │   │   │       ├── users/page.tsx
│   │   │   │       └── stages/page.tsx
│   │   │   ├── layout.tsx
│   │   │   ├── providers.tsx
│   │   │   └── globals.css
│   │   ├── components/
│   │   │   ├── ui/
│   │   │   ├── layout/
│   │   │   ├── leads/
│   │   │   ├── deals/
│   │   │   ├── pipeline/
│   │   │   ├── tasks/
│   │   │   └── charts/
│   │   ├── features/
│   │   │   ├── auth/
│   │   │   ├── leads/
│   │   │   ├── deals/
│   │   │   ├── pipeline/
│   │   │   ├── tasks/
│   │   │   └── analytics/
│   │   ├── lib/
│   │   │   ├── api-client.ts
│   │   │   ├── query-client.ts
│   │   │   ├── auth.ts
│   │   │   ├── env.ts
│   │   │   └── utils.ts
│   │   ├── hooks/
│   │   ├── types/
│   │   └── middleware.ts
│   └── Dockerfile
└── .github/
    └── workflows/
        ├── backend-ci.yml
        └── frontend-ci.yml