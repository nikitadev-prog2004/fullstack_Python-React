"use client";

import { Badge, Button, Card, Spinner, Table } from "react-bootstrap";
import { filesApi } from "../entities/file/api";
import { ProcessingBadge } from "../entities/file/ui/ProcessingBadge";
import { ScanCell } from "../entities/file/ui/ScanCell";
import { FileItem } from "../entities/file/types";
import { formatDate, formatSize } from "../shared/lib/format";

type Props = {
  files: FileItem[];
  isLoading: boolean;
};

export function FilesTable({ files, isLoading }: Props) {
  return (
    <Card className="shadow-sm border-0 mb-4">
      <Card.Header className="bg-white border-0 pt-4 px-4">
        <div className="d-flex justify-content-between align-items-center">
          <h2 className="h5 mb-0">Файлы</h2>
          <Badge bg="secondary">{files.length}</Badge>
        </div>
      </Card.Header>
      <Card.Body className="px-4 pb-4">
        {isLoading ? (
          <div className="d-flex justify-content-center py-5">
            <Spinner animation="border" />
          </div>
        ) : (
          <div className="table-responsive">
            <Table hover bordered className="align-middle mb-0">
              <thead className="table-light">
                <tr>
                  <th>Название</th>
                  <th>Файл</th>
                  <th>MIME</th>
                  <th>Размер</th>
                  <th>Статус</th>
                  <th>Проверка</th>
                  <th>Создан</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {files.length === 0 ? (
                  <tr>
                    <td colSpan={8} className="text-center py-4 text-secondary">
                      Файлы пока не загружены
                    </td>
                  </tr>
                ) : (
                  files.map((file) => (
                    <tr key={file.id}>
                      <td>
                        <div className="fw-semibold">{file.title}</div>
                        <div className="small text-secondary">{file.id}</div>
                      </td>
                      <td>{file.original_name}</td>
                      <td>{file.mime_type}</td>
                      <td>{formatSize(file.size)}</td>
                      <td>
                        <ProcessingBadge status={file.processing_status} />
                      </td>
                      <td>
                        <ScanCell
                          scan_status={file.scan_status}
                          scan_details={file.scan_details}
                          requires_attention={file.requires_attention}
                        />
                      </td>
                      <td>{formatDate(file.created_at)}</td>
                      <td className="text-nowrap">
                        <Button
                          as="a"
                          href={filesApi.downloadUrl(file.id)}
                          variant="outline-primary"
                          size="sm"
                        >
                          Скачать
                        </Button>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </Table>
          </div>
        )}
      </Card.Body>
    </Card>
  );
}
