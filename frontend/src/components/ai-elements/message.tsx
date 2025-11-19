"use client";

import { cn } from "@/lib/utils";
import type { ComponentProps } from "react";

export type MessageRole = "user" | "assistant" | "system" | "other";

export type MessageProps = ComponentProps<"div"> & {
  from: MessageRole;
};

export const Message = ({ from, className, children, ...props }: MessageProps) => {
  const isUser = from === "user";
  const isAssistant = from === "assistant";
  const isSystem = from === "system";

  return (
    <div
      className={cn(
        "flex w-full gap-3 mb-4",
        isUser && "justify-end",
        isAssistant && "justify-start",
        isSystem && "justify-center",
        !isUser && !isAssistant && !isSystem && "justify-start",
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
};

export type MessageContentProps = ComponentProps<"div">;

export const MessageContent = ({ className, children, ...props }: MessageContentProps) => {
  return (
    <div
      className={cn("flex flex-col gap-1 max-w-[80%]", className)}
      {...props}
    >
      {children}
    </div>
  );
};

export type MessageResponseProps = ComponentProps<"div"> & {
  from?: MessageRole;
};

export const MessageResponse = ({ from = "assistant", className, children, ...props }: MessageResponseProps) => {
  const isUser = from === "user";
  const isAssistant = from === "assistant";
  const isSystem = from === "system";

  return (
    <div
      className={cn(
        "rounded-lg px-4 py-2 text-sm",
        isUser && "bg-primary text-primary-foreground",
        isAssistant && "bg-muted text-foreground",
        isSystem && "bg-muted/50 text-muted-foreground text-center text-xs",
        !isUser && !isAssistant && !isSystem && "bg-muted text-foreground",
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
};

