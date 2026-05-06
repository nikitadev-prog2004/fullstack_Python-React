"use client";

import { useCallback, useState } from "react";
import { Alert, Col, Container, Row } from "react-bootstrap";

import { useAlerts } from "../entities/alert/hooks";
import { useFiles } from "../entities/file/hooks";
import { UploadFileModal } from "../features/upload-file/UploadFileModal";
import { AlertsTable } from "../widgets/AlertsTable";
import { FilesTable } from "../widgets/FilesTable";
import { PageHeader } from "../widgets/PageHeader";

export default function Page() {
  const files = useFiles();
  const alerts = useAlerts();
  const [showModal, setShowModal] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const reloadAll = useCallback(async () => {
    setErrorMessage(null);
    await Promise.all([files.reload(), alerts.reload()]);
  }, [files, alerts]);

  const isLoading = files.isLoading || alerts.isLoading;
  const fetchError = files.error ?? alerts.error;
  const displayedError = errorMessage ?? fetchError;

  return (
    <Container fluid className="py-4 px-4 bg-light min-vh-100">
      <Row className="justify-content-center">
        <Col xxl={10} xl={11}>
          <PageHeader
            onRefresh={() => void reloadAll()}
            onAdd={() => setShowModal(true)}
          />

          {displayedError ? (
            <Alert variant="danger" className="shadow-sm">
              {displayedError}
            </Alert>
          ) : null}

          <FilesTable files={files.data} isLoading={isLoading} />
          <AlertsTable alerts={alerts.data} isLoading={isLoading} />
        </Col>
      </Row>

      <UploadFileModal
        show={showModal}
        onHide={() => setShowModal(false)}
        onUploaded={() => {
          setShowModal(false);
          void reloadAll();
        }}
        onError={(message) => setErrorMessage(message)}
      />
    </Container>
  );
}
