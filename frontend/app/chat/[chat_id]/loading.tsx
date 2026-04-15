export default function Loading() {
  return (
    <div className="flex-1 flex flex-col h-full bg-white dark:bg-zinc-950">
      <div className="flex-1 overflow-y-auto p-4 md:p-8 space-y-6">
        <div className="max-w-3xl mx-auto space-y-6">
          {[1, 2, 3].map((i) => (
            <div key={i} className={`flex ${i % 2 === 0 ? 'justify-end' : 'justify-start'}`}>
              <div className={`h-16 w-2/3 rounded-2xl animate-pulse ${i % 2 === 0 ? 'bg-blue-100 dark:bg-blue-900/20' : 'bg-zinc-100 dark:bg-zinc-800'}`} />
            </div>
          ))}
        </div>
      </div>
      <div className="p-4 md:p-8">
        <div className="max-w-3xl mx-auto h-14 bg-zinc-100 dark:bg-zinc-800 rounded-2xl animate-pulse" />
      </div>
    </div>
  );
}