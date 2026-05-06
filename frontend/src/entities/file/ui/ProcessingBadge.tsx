import { Badge } from "react-bootstrap";

const variantByStatus: Record<string, string> = {
  failed: "danger",
  processing: "warning",
  processed: "success",
};

export function ProcessingBadge({ status }: { status: string }) {
  const variant = variantByStatus[status] ?? "secondary";
  return <Badge bg={variant}>{status}</Badge>;
}
