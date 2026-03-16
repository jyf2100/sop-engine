"use client";

import { useState, useEffect, useCallback } from "react";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import { AlertCircle, Check, RefreshCw } from "lucide-react";

interface JsonEditorProps<T extends object> {
  value: T;
  onChange: (value: T) => void;
  onError?: (error: string | null) => void;
  height?: string;
  readOnly?: boolean;
}

export function JsonEditor<T extends object>({
  value,
  onChange,
  onError,
  height = "200px",
  readOnly = false,
}: JsonEditorProps<T>) {
  const [text, setText] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isValid, setIsValid] = useState(true);

  // 同步外部 value 到 text
  useEffect(() => {
    try {
      const formatted = JSON.stringify(value, null, 2);
      setText(formatted);
      setError(null);
      setIsValid(true);
    } catch (e) {
      console.error("Failed to stringify value:", e);
    }
  }, [value]);

  // 解析并验证 JSON
  const validateAndParse = useCallback(
    (jsonText: string) => {
      if (!jsonText.trim()) {
        setError(null);
        setIsValid(true);
        onChange({} as T);
        onError?.(null);
        return;
      }

      try {
        const parsed = JSON.parse(jsonText);
        setError(null);
        setIsValid(true);
        onChange(parsed as T);
        onError?.(null);
      } catch (e) {
        const errorMessage =
          e instanceof Error ? e.message : "JSON 格式错误";
        setError(errorMessage);
        setIsValid(false);
        onError?.(errorMessage);
      }
    },
    [onChange, onError]
  );

  // 处理文本变化
  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const newText = e.target.value;
    setText(newText);
    validateAndParse(newText);
  };

  // 格式化 JSON
  const formatJson = () => {
    try {
      const parsed = JSON.parse(text);
      const formatted = JSON.stringify(parsed, null, 2);
      setText(formatted);
      setError(null);
      setIsValid(true);
    } catch (e) {
      // 无法格式化，保持原样
    }
  };

  // 重置为原始值
  const reset = () => {
    try {
      const formatted = JSON.stringify(value, null, 2);
      setText(formatted);
      setError(null);
      setIsValid(true);
    } catch (e) {
      console.error("Failed to reset:", e);
    }
  };

  return (
    <div className="space-y-2">
      <div className="relative">
        <Textarea
          value={text}
          onChange={handleChange}
          className={`font-mono text-sm ${height} ${
            error
              ? "border-red-500 focus-visible:ring-red-500"
              : isValid
              ? "border-green-500"
              : ""
          }`}
          placeholder='{"key": "value"}'
          readOnly={readOnly}
        />
        <div className="absolute top-2 right-2 flex items-center gap-1">
          {isValid && !error && text.trim() && (
            <Check className="h-4 w-4 text-green-500" />
          )}
          {error && <AlertCircle className="h-4 w-4 text-red-500" />}
        </div>
      </div>

      {error && (
        <div className="text-xs text-red-500 flex items-center gap-1">
          <AlertCircle className="h-3 w-3" />
          {error}
        </div>
      )}

      {!readOnly && (
        <div className="flex gap-2">
          <Button
            type="button"
            variant="outline"
            size="sm"
            onClick={formatJson}
            disabled={!text.trim()}
          >
            格式化
          </Button>
          <Button
            type="button"
            variant="outline"
            size="sm"
            onClick={reset}
          >
            <RefreshCw className="h-3 w-3 mr-1" />
            重置
          </Button>
        </div>
      )}
    </div>
  );
}
