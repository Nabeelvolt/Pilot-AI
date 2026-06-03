export default function TopBar({ title }: { title: string }) {
  return (
    <div className="bg-white border-b border-slate-200 px-8 py-5 sticky top-0 z-10">
      <h1 className="text-2xl font-bold text-slate-800">{title}</h1>
    </div>
  );
}
