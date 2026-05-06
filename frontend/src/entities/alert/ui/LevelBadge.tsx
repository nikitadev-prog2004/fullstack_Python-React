import { Badge } from "react-bootstrap";

const variantByLevel: Record<string, string> = {
  critical: "danger",
  warning: "warning",
};

export function LevelBadge({ level }: { level: string }) {
  return <Badge bg={variantByLevel[level] ?? "success"}>{level}</Badge>;
}
