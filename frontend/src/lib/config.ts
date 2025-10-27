export const apiBaseUrl =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api/v1";

export const realtimeSocketUrl =
  process.env.NEXT_PUBLIC_WEB_SOCKET_URL ?? "ws://localhost:8000/ws";
