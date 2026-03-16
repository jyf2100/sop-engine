import Link from "next/link";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

export default function Home() {
  return (
    <div className="min-h-screen bg-zinc-50 dark:bg-zinc-950">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <header className="mb-8">
          <h1 className="text-3xl font-bold text-zinc-900 dark:text-zinc-50">
            SOP Engine
          </h1>
          <p className="text-zinc-600 dark:text-zinc-400 mt-2">
            标准作业流程编排引擎 - 基于 OpenClaw 的工作流自动化平台
          </p>
        </header>

        {/* Main Content */}
        <main className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {/* Templates Card */}
          <Card className="hover:shadow-lg transition-shadow cursor-pointer">
            <Link href="/templates">
              <CardHeader>
                <CardTitle>流程模板</CardTitle>
                <CardDescription>管理和编辑 YAML 流程模板</CardDescription>
              </CardHeader>
              <CardContent>
                <Button variant="outline" className="w-full">
                  查看模板
                </Button>
              </CardContent>
            </Link>
          </Card>

          {/* Executions Card */}
          <Card className="hover:shadow-lg transition-shadow cursor-pointer">
            <Link href="/executions">
              <CardHeader>
                <CardTitle>执行监控</CardTitle>
                <CardDescription>查看和监控流程执行状态</CardDescription>
              </CardHeader>
              <CardContent>
                <Button variant="outline" className="w-full">
                  查看执行
                </Button>
              </CardContent>
            </Link>
          </Card>

          {/* Approvals Card */}
          <Card className="hover:shadow-lg transition-shadow cursor-pointer">
            <Link href="/approvals">
              <CardHeader>
                <CardTitle>审批工作台</CardTitle>
                <CardDescription>处理待审批的人工节点</CardDescription>
              </CardHeader>
              <CardContent>
                <Button variant="outline" className="w-full">
                  待审批
                </Button>
              </CardContent>
            </Link>
          </Card>

          {/* Agents Card */}
          <Card className="hover:shadow-lg transition-shadow cursor-pointer">
            <Link href="/agents">
              <CardHeader>
                <CardTitle>Agent 管理</CardTitle>
                <CardDescription>配置和管理 OpenClaw Agent</CardDescription>
              </CardHeader>
              <CardContent>
                <Button variant="outline" className="w-full">
                  管理 Agent
                </Button>
              </CardContent>
            </Link>
          </Card>

          {/* Flow Editor Card */}
          <Card className="hover:shadow-lg transition-shadow cursor-pointer">
            <Link href="/editor">
              <CardHeader>
                <CardTitle>流程编辑器</CardTitle>
                <CardDescription>可视化编辑流程模板</CardDescription>
              </CardHeader>
              <CardContent>
                <Button variant="outline" className="w-full">
                  打开编辑器
                </Button>
              </CardContent>
            </Link>
          </Card>

          {/* Settings Card */}
          <Card className="opacity-50">
            <CardHeader>
              <CardTitle>系统设置</CardTitle>
              <CardDescription>配置 OpenClaw 和系统参数</CardDescription>
            </CardHeader>
            <CardContent>
              <Button variant="outline" className="w-full" disabled>
                即将推出
              </Button>
            </CardContent>
          </Card>
        </main>
      </div>
    </div>
  );
}
