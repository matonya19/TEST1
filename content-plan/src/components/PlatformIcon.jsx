const PATHS = {
  Instagram: (
    <>
      <rect x="3" y="3" width="14" height="14" rx="4" />
      <circle cx="10" cy="10" r="3.2" />
      <circle cx="14.2" cy="5.8" r="0.6" fill="currentColor" stroke="none" />
    </>
  ),
  Telegram: (
    <path d="M3 10.4 16.5 4.2c.6-.28 1.2.18 1 .84l-2.4 11.2c-.16.72-.9 1-1.46.58l-3.4-2.6-1.8 1.7c-.2.2-.5.1-.55-.18l-.4-2.9L3.7 11c-.6-.2-.6-1.02.3-1.24Z" />
  ),
  Threads: (
    <>
      <circle cx="10" cy="10" r="7" />
      <path d="M8 7.2c2.6-.4 4.2.7 4.2 3 0 2.4-2 3.4-3.6 3.2-1.3-.16-2.1-1-1.9-2 .2-1 1.3-1.3 2.6-1.2 1.6.14 2.5.9 2.4 2.1" fill="none" />
    </>
  ),
  YouTube: (
    <>
      <rect x="2.5" y="5" width="15" height="10" rx="3" />
      <path d="M8.5 8v4l3.6-2Z" fill="currentColor" stroke="none" />
    </>
  ),
  TikTok: (
    <path d="M11 3v8.3a2.4 2.4 0 1 1-2-2.36V7a4.4 4.4 0 1 0 4 4.38V8.2a5 5 0 0 0 3-1V5.1a5 5 0 0 1-3-1.6V3Z" />
  ),
  VK: (
    <>
      <rect x="2.5" y="4" width="15" height="12" rx="3" />
      <path d="M6.2 7.5c.2 3 1.7 4.8 4 4.9v-1.8c.9.1 1.3.7 1.7 1.8h1.8c-.2-1.2-1-1.9-1.6-2.3.6-.4 1.3-1.2 1.5-2.2h-1.6c-.3 1-1 1.8-1.5 1.9v-1.9H8.9v3c-.7-.4-1.3-1.5-1.4-3Z" fill="currentColor" stroke="none" />
    </>
  ),
};

export default function PlatformIcon({ platform, size = 16 }) {
  const path = PATHS[platform];
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 20 20"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.3"
      strokeLinejoin="round"
      strokeLinecap="round"
      aria-hidden="true"
    >
      {path}
    </svg>
  );
}
