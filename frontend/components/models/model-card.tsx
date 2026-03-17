"use client";

import { ModelConfig } from "@/lib/api-client";
import { cn } from "@/lib/utils";

interface ModelCardProps {
  model: ModelConfig;
  onEdit: (model: ModelConfig) => void;
  onDelete: (model: ModelConfig) => void;
  onSetDefault: (model: ModelConfig) => void;
}

// 霓虹赛博朋克配色方案
const providerColors: Record<string, { bar: string; badge: string; glow: string }> = {
  anthropic: {
    bar: "bg-gradient-to-r from-orange-500 via-amber-400 to-yellow-500",
    badge: "bg-gradient-to-r from-orange-600 to-amber-500 text-white shadow-[0_0_15px_rgba(249,115,22,0.5)]",
    glow: "hover:shadow-[0_0_30px_rgba(249,115,22,0.3)]",
  },
  openai: {
    bar: "bg-gradient-to-r from-emerald-400 via-teal-400 to-cyan-400",
    badge: "bg-gradient-to-r from-emerald-500 to-teal-400 text-white shadow-[0_0_15px_rgba(16,185,129,0.5)]",
    glow: "hover:shadow-[0_0_30px_rgba(16,185,129,0.3)]",
  },
  google: {
    bar: "bg-gradient-to-r from-blue-500 via-sky-400 to-cyan-400",
    badge: "bg-gradient-to-r from-blue-600 to-sky-500 text-white shadow-[0_0_15px_rgba(59,130,246,0.5)]",
    glow: "hover:shadow-[0_0_30px_rgba(59,130,246,0.3)]",
  },
  cohere: {
    bar: "bg-gradient-to-r from-violet-500 via-purple-400 to-fuchsia-400",
    badge: "bg-gradient-to-r from-violet-600 to-purple-500 text-white shadow-[0_0_15px_rgba(139,92,246,0.5)]",
    glow: "hover:shadow-[0_0_30px_rgba(139,92,246,0.3)]",
  },
  stability: {
    bar: "bg-gradient-to-r from-pink-500 via-rose-400 to-red-400",
    badge: "bg-gradient-to-r from-pink-600 to-rose-500 text-white shadow-[0_0_15px_rgba(236,72,153,0.5)]",
    glow: "hover:shadow-[0_0_30px_rgba(236,72,153,0.3)]",
  },
  custom: {
    bar: "bg-gradient-to-r from-zinc-500 via-slate-400 to-gray-400",
    badge: "bg-gradient-to-r from-zinc-600 to-slate-500 text-white shadow-[0_0_15px_rgba(113,113,122,0.5)]",
    glow: "hover:shadow-[0_0_30px_rgba(113,113,122,0.3)]",
  },
};

const typeIcons: Record<string, string> = {
  llm: "🧠",
  embedding: "🔢",
  image: "🎨",
};

const typeGradients: Record<string, string> = {
  llm: "from-violet-500/10 via-purple-500/5 to-fuchsia-500/10",
  embedding: "from-cyan-500/10 via-teal-500/5 to-emerald-500/10",
  image: "from-pink-500/10 via-rose-500/5 to-orange-500/10",
};

export function ModelCard({ model, onEdit, onDelete, onSetDefault }: ModelCardProps) {
  const colors = providerColors[model.provider] || providerColors.custom;
  const typeIcon = typeIcons[model.type] || "⚙️";
  const typeGradient = typeGradients[model.type] || typeGradients.custom;

  return (
    <div
      className={cn(
        "group relative overflow-hidden rounded-2xl border transition-all duration-500",
        "backdrop-blur-sm",
        model.is_default
          ? "border-amber-400/50 dark:border-amber-500/50 shadow-[0_0_40px_rgba(245,158,11,0.2)]"
          : "border-zinc-200/50 dark:border-zinc-700/50",
        colors.glow
      )}
    >
      {/* Background gradient */}
      <div className={cn(
        "absolute inset-0 bg-gradient-to-br opacity-50",
        model.is_default
          ? "from-amber-500/20 via-orange-500/10 to-yellow-500/20"
          : typeGradient
      )} />

      {/* Default badge - 金色星光效果 */}
      {model.is_default && (
        <div className="absolute top-3 right-3 z-10">
          <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-bold
            bg-gradient-to-r from-amber-400 via-yellow-400 to-orange-400 text-zinc-900
            shadow-[0_0_20px_rgba(245,158,11,0.6)]
            animate-pulse">
            ⭐ 默认
          </span>
        </div>
      )}

      {/* Provider color bar - 霓虹渐变 */}
      <div className={cn("h-2 w-full rounded-t-xl", colors.bar)} />

      <div className="relative p-5">
        {/* Header */}
        <div className="flex items-start gap-3 mb-4">
          <span className="text-3xl drop-shadow-lg">{typeIcon}</span>
          <div className="flex-1 min-w-0">
            <h3 className="font-bold text-lg truncate bg-gradient-to-r from-zinc-900 to-zinc-700 dark:from-white dark:to-zinc-300 bg-clip-text text-transparent">
              {model.name}
            </h3>
            <p className="text-sm text-zinc-500 dark:text-zinc-400 font-mono">
              {model.model_id}
            </p>
          </div>
        </div>

        {/* Meta info */}
        <div className="space-y-3 mb-4">
          <div className="flex items-center gap-2 text-sm">
            <span className="text-zinc-400">Provider</span>
            <span className={cn("px-2.5 py-1 rounded-lg text-xs font-bold uppercase tracking-wide", colors.badge)}>
              {model.provider}
            </span>
          </div>

          {model.dimensions && (
            <div className="flex items-center gap-2 text-sm">
              <span className="text-zinc-400">Dimensions</span>
              <span className="px-2 py-0.5 rounded-md bg-cyan-100 dark:bg-cyan-900/40 text-cyan-700 dark:text-cyan-300 font-mono text-xs">
                {model.dimensions}
              </span>
            </div>
          )}

          {model.default_size && (
            <div className="flex items-center gap-2 text-sm">
              <span className="text-zinc-400">Size</span>
              <span className="px-2 py-0.5 rounded-md bg-pink-100 dark:bg-pink-900/40 text-pink-700 dark:text-pink-300 font-mono text-xs">
                {model.default_size}
              </span>
            </div>
          )}

          <div className="flex items-center gap-2 text-sm">
            <span className="text-zinc-400">Base URL</span>
            <span className="font-mono text-xs text-zinc-400 truncate max-w-[180px]">
              {model.base_url}
            </span>
          </div>
        </div>

        {/* Default params preview - 彩色标签 */}
        {Object.keys(model.default_params).length > 0 && (
          <div className="mb-4 p-3 rounded-xl bg-zinc-900/5 dark:bg-white/5 backdrop-blur-sm border border-zinc-200/50 dark:border-zinc-700/50">
            <div className="text-xs text-zinc-500 mb-2 font-medium">默认参数</div>
            <div className="flex flex-wrap gap-2">
              {model.default_params.temperature !== undefined && (
                <span className="px-2.5 py-1 rounded-lg bg-gradient-to-r from-amber-400/20 to-orange-400/20 text-amber-700 dark:text-amber-300 text-xs font-mono font-medium border border-amber-400/30">
                  temp: {model.default_params.temperature}
                </span>
              )}
              {model.default_params.max_tokens !== undefined && (
                <span className="px-2.5 py-1 rounded-lg bg-gradient-to-r from-cyan-400/20 to-blue-400/20 text-cyan-700 dark:text-cyan-300 text-xs font-mono font-medium border border-cyan-400/30">
                  tokens: {model.default_params.max_tokens}
                </span>
              )}
              {model.default_params.top_p !== undefined && (
                <span className="px-2.5 py-1 rounded-lg bg-gradient-to-r from-emerald-400/20 to-teal-400/20 text-emerald-700 dark:text-emerald-300 text-xs font-mono font-medium border border-emerald-400/30">
                  top_p: {model.default_params.top_p}
                </span>
              )}
              {model.default_params.quality !== undefined && (
                <span className="px-2.5 py-1 rounded-lg bg-gradient-to-r from-violet-400/20 to-purple-400/20 text-violet-700 dark:text-violet-300 text-xs font-mono font-medium border border-violet-400/30">
                  quality: {model.default_params.quality}
                </span>
              )}
            </div>
          </div>
        )}

        {/* Actions */}
        <div className="flex items-center gap-2 pt-3 border-t border-zinc-200/50 dark:border-zinc-700/50">
          <button
            onClick={() => onEdit(model)}
            className="flex-1 px-4 py-2.5 text-sm font-semibold rounded-xl
              bg-zinc-100 dark:bg-zinc-800 hover:bg-zinc-200 dark:hover:bg-zinc-700
              transition-all duration-300 hover:scale-[1.02]"
          >
            编辑
          </button>
          {!model.is_default && (
            <button
              onClick={() => onSetDefault(model)}
              className="px-4 py-2.5 text-sm font-semibold rounded-xl
                bg-gradient-to-r from-amber-400 to-orange-400 text-zinc-900
                hover:from-amber-500 hover:to-orange-500
                shadow-[0_0_15px_rgba(245,158,11,0.3)]
                hover:shadow-[0_0_25px_rgba(245,158,11,0.5)]
                transition-all duration-300 hover:scale-[1.02]"
            >
              设为默认
            </button>
          )}
          <button
            onClick={() => onDelete(model)}
            className="px-4 py-2.5 text-sm font-semibold rounded-xl
              text-rose-500 hover:bg-rose-50 dark:hover:bg-rose-900/20
              hover:text-rose-600 dark:hover:text-rose-400
              transition-all duration-300 hover:scale-[1.02]"
          >
            删除
          </button>
        </div>
      </div>
    </div>
  );
}
