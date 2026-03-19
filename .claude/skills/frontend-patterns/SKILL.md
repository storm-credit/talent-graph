---
name: frontend-patterns
description: TalentGraph React 프론트엔드 패턴과 컨벤션
---

# 프론트엔드 패턴

## 기술 스택
- React 19 + TypeScript
- Vite (빌드/HMR)
- Tailwind CSS (다크 테마, zinc 계열)
- shadcn/ui (기본 컴포넌트)
- Nivo (차트)
- React Flow (그래프 시각화)
- Framer Motion (애니메이션)

## 디자인 시스템
- 다크 모드 기본: `bg-zinc-950`, `bg-zinc-900`, `bg-zinc-800`
- 텍스트: `text-white`, `text-zinc-400`
- 보더: `border-zinc-700`, `border-zinc-800`
- 액센트: `text-blue-400`, `text-emerald-400`
- 카드: `bg-zinc-900 border border-zinc-800 rounded-2xl p-5`

## 컴포넌트 패턴

### 페이지 레이아웃
```tsx
export default function SomePage() {
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">제목</h1>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* 카드들 */}
      </div>
    </div>
  );
}
```

### API 호출
```tsx
const [data, setData] = useState<Type[]>([]);
useEffect(() => {
  api.getData().then(setData);
}, []);
```

### 모달
```tsx
{showModal && (
  <div className="fixed inset-0 bg-black/60 z-50 flex items-center justify-center p-4"
       onClick={() => setShowModal(false)}>
    <div className="bg-zinc-900 border border-zinc-700 rounded-2xl w-full max-w-md p-5"
         onClick={e => e.stopPropagation()}>
      {/* 내용 */}
    </div>
  </div>
)}
```

## 다국어 (i18n)
- `frontend/src/i18n/ko.json` — 한국어
- `frontend/src/i18n/en.json` — 영어
- 새 텍스트 추가 시 두 파일 모두 업데이트

## 라우팅
- `App.tsx`에서 React Router 사용
- 새 페이지 추가: 1) 페이지 컴포넌트 생성 → 2) App.tsx에 Route 추가 → 3) AppShell.tsx에 네비 추가 → 4) i18n 키 추가
