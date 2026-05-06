import { Badge } from "react-bootstrap";
import { FileItem } from "../types";

type Props = Pick<FileItem, "scan_status" | "scan_details" | "requires_attention">;

export function ScanCell({ scan_status, scan_details, requires_attention }: Props) {
  return (
    <div className="d-flex flex-column gap-1">
      <Badge bg={requires_attention ? "warning" : "success"}>
        {scan_status ?? "pending"}
      </Badge>
      <span className="small text-secondary">
        {scan_details ?? "Ожидает обработки"}
      </span>
    </div>
  );
}
