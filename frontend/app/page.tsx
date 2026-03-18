import Link from "next/link";
import { cn } from "@/lib/utils";

const navCards = [
  {
    title: "流程模板",
    description: "管理和编辑 YAML 流程模板",
    icon: "📋",
    href: "/templates",
    gradient: "from-blue-500 to-cyan-400",
    glow: "rgba(59, 130, 246, 0.4)",
  },
  {
    title: "执行监控",
    description: "查看和监控流程执行状态",
    icon: "📊",
    href: "/executions",
    gradient: "from-emerald-500 to-teal-400",
    glow: "rgba(16, 185, 129, 0.4)",
  },
  {
    title: "审批工作台",
    description: "处理待审批的人工节点",
    icon: "✅",
    href: "/approvals",
    gradient: "from-amber-500 to-orange-400",
    glow: "rgba(245, 158, 11, 0.4)",
  },
  {
    title: "Agent 管理",
    description: "配置和管理 OpenClaw Agent",
    icon: "🤖",
    href: "/agents",
    gradient: "from-violet-500 to-purple-400",
    glow: "rgba(139, 92, 246, 0.4)",
  },
  {
    title: "模型配置",
    description: "管理 LLM/Embedding/图像模型",
    icon: "🧠",
    href: "/models",
    gradient: "from-fuchsia-500 to-pink-400",
    glow: "rgba(217, 70, 239, 0.4)",
    featured: true,
  },
  {
    title: "流程编辑器",
    description: "可视化编辑流程模板",
    icon: "🎨",
    href: "/editor",
    gradient: "from-rose-500 to-red-400",
    glow: "rgba(244, 63, 94, 0.4)",
  },
];

export default function Home() {
  return (
    <div className="min-h-screen relative overflow-hidden">
      {/* 装饰性背景光晕 */}
      <div className="fixed inset-0 bg-zinc-50 dark:bg-zinc-950">
        <div className="absolute top-0 left-1/4 w-[600px] h-[600px] bg-gradient-to-br from-violet-500/20 via-purple-500/10 to-transparent rounded-full blur-3xl" />
        <div className="absolute bottom-0 right-1/4 w-[600px] h-[600px] bg-gradient-to-tl from-cyan-500/20 via-teal-500/10 to-transparent rounded-full blur-3xl" />
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-gradient-to-r from-fuchsia-500/10 via-pink-500/5 to-violet-500/10 rounded-full blur-3xl" />
      </div>

      <div className="container mx-auto px-4 py-12 relative">
        {/* Header */}
        <header className="text-center mb-16">
          <div className="inline-flex items-center justify-center mb-4">
            <h1 className="text-5xl md:text-6xl font-black tracking-tight
              bg-gradient-to-r from-violet-600 via-fuchsia-500 to-cyan-400
              bg-clip-text text-transparent drop-shadow-2xl">
              SOP Engine
            </h1>
          </div>
          <p className="text-xl text-zinc-600 dark:text-zinc-400 max-w-2xl mx-auto leading-relaxed">
            标准作业流程编排引擎
            <span className="text-zinc-400 dark:text-zinc-500 mx-2">·</span>
            基于 OpenClaw 的工作流自动化平台
          </p>

          {/* Stats badges */}
          <div className="flex items-center justify-center gap-4 mt-8">
            {["多模型支持", "可视化编辑", "实时监控", "人工审批"].map((feature, i) => (
              <span
                key={feature}
                className={cn(
                  "px-3 py-1.5 text-sm font-medium rounded-full",
                  "bg-zinc-900/5 dark:bg-white/5 backdrop-blur-sm",
                  "border border-zinc-200/50 dark:border-zinc-700/50",
                  "text-zinc-600 dark:text-zinc-400"
                )}
              >
                {["✨", "🎨", "📊", "✅"][i]} {feature}
              </span>
            ))}
          </div>
        </header>

        {/* Main Content */}
        <main className="grid gap-5 md:grid-cols-2 lg:grid-cols-3 max-w-6xl mx-auto">
          {navCards.map((card) => (
            <Link
              key={card.href}
              href={card.href}
              className={cn(
                "group relative overflow-hidden rounded-2xl p-6 transition-all duration-500",
                "bg-white/80 dark:bg-zinc-900/80 backdrop-blur-xl",
                "border-2 hover:border-transparent",
                "hover:shadow-2xl hover:scale-[1.02]",
                card.featured
                  ? "border-fuchsia-200 dark:border-fuchsia-800/50 hover:shadow-[0_0_40px_rgba(217,70,239,0.3)]"
                  : "border-zinc-200/50 dark:border-zinc-700/50"
              )}
            >
              {/* Gradient overlay */}
              <div className={cn(
                "absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-500",
                `bg-gradient-to-br ${card.gradient}`,
                card.featured && "opacity-10"
              )} />

              {/* Glow effect */}
              <div
                className="absolute -inset-1 opacity-0 group-hover:opacity-100 transition-opacity duration-500 blur-xl -z-10"
                style={{ background: `radial-gradient(circle, ${card.glow}, transparent 70%)` }}
              />

              {/* Content */}
              <div className="relative">
                <div className="flex items-start justify-between mb-4">
                  <span className="text-4xl drop-shadow-lg">{card.icon}</span>
                  {card.featured && (
                    <span className="px-2 py-1 text-xs font-bold rounded-full
                      bg-gradient-to-r from-fuchsia-500 to-pink-500 text-white
                      shadow-[0_0_10px_rgba(217,70,239,0.5)]">
                      NEW
                    </span>
                  )}
                </div>

                <h2 className={cn(
                  "text-xl font-bold mb-2 transition-colors duration-300",
                  `text-zinc-900 dark:text-white group-hover:bg-gradient-to-r group-hover:bg-clip-text group-hover:text-transparent`,
                  `group-hover:${card.gradient}`
                )}>
                  {card.title}
                </h2>
                <p className="text-zinc-500 dark:text-zinc-400 text-sm">
                  {card.description}
                </p>

                <div className="mt-4 flex items-center text-sm font-semibold text-zinc-400 group-hover:text-zinc-600 dark:group-hover:text-zinc-300 transition-colors">
                  <span>前往</span>
                  <svg
                    className="ml-1 w-4 h-4 transform group-hover:translate-x-1 transition-transform"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                </div>
              </div>
            </Link>
          ))}
        </main>

        {/* Footer */}
        <footer className="text-center mt-16 text-zinc-400 dark:text-zinc-500 text-sm">
          <p>SOP Engine v0.1.0 · Powered by OpenClaw</p>
        </footer>
      </div>
    </div>
  );
}
