"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";

const navItems = [
  { href: "/", label: "首页", icon: "🏠" },
  { href: "/templates", label: "模板", icon: "📋" },
  { href: "/executions", label: "执行", icon: "📊" },
  { href: "/approvals", label: "审批", icon: "✅" },
  { href: "/agents", label: "Agent", icon: "🤖" },
  { href: "/models", label: "模型", icon: "🧠" },
  { href: "/channels", label: "Channel", icon: "📡" },
  { href: "/editor", label: "编辑器", icon: "🎨" },
];

export function Nav() {
  const pathname = usePathname();

  return (
    <nav className={cn(
      "sticky top-0 z-50",
      "border-b bg-white/80 dark:bg-zinc-950/80 backdrop-blur-xl",
      "border-zinc-200/50 dark:border-zinc-800/50",
      "shadow-lg"
    )}>
      <div className="container mx-auto px-4">
        <div className="flex h-14 items-center justify-between">
          <Link href="/" className="group flex items-center gap-2">
            <div className={cn(
              "w-8 h-8 rounded-lg",
              "bg-gradient-to-br from-violet-500 to-purple-600",
              "flex items-center justify-center",
              "shadow-[0_0_10px_rgba(139,92,246,0.3)]"
            )}>
              <span className="text-white text-xs font-black">S</span>
            </div>
            <span className="font-bold text-lg bg-gradient-to-r from-zinc-900 to-zinc-700 dark:from-white dark:to-zinc-200 bg-clip-text text-transparent">
              SOP Engine
            </span>
          </Link>
          <div className="flex space-x-1">
            {navItems.map((item) => {
              const isActive = pathname === item.href;
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={cn(
                    "relative px-3 py-2 rounded-xl text-sm font-medium transition-all duration-300",
                    "hover:scale-[1.02]",
                    isActive
                      ? "text-white shadow-lg"
                      : "text-zinc-600 dark:text-zinc-400 hover:text-zinc-900 dark:hover:text-zinc-200"
                  )}
                  style={isActive ? {
                    background: "linear-gradient(135deg, #8b5cf6 0%, #a855f7 50%, #ec4899 100%)",
                    boxShadow: "0 0 20px rgba(139, 92, 246, 0.4)",
                  } : undefined}
                >
                  <span className="mr-1.5">{item.icon}</span>
                  {item.label}
                  {isActive && (
                    <span className="absolute -bottom-0.5 left-1/2 -translate-x-1/2 w-1 h-1 rounded-full bg-white/50" />
                  )}
                </Link>
              );
            })}
          </div>
        </div>
      </div>
    </nav>
  );
}
