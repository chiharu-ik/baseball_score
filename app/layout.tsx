import "./globals.css";

export const metadata = {
  title: "Baseball Score",
  description: "スマホ専用 野球スコア・成績管理",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="ja">
      <body>{children}</body>
    </html>
  );
}
