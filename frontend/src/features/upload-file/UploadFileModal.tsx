"use client";

import { FormEvent, useState } from "react";
import { Button, Form, Modal } from "react-bootstrap";
import { useUploadFile } from "./hooks";

type Props = {
  show: boolean;
  onHide: () => void;
  onUploaded: () => void;
  onError: (message: string) => void;
};

export function UploadFileModal({ show, onHide, onUploaded, onError }: Props) {
  const [title, setTitle] = useState("");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const { upload, isSubmitting } = useUploadFile();

  const reset = () => {
    setTitle("");
    setSelectedFile(null);
  };

  const handleClose = () => {
    if (isSubmitting) return;
    reset();
    onHide();
  };

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!title.trim() || !selectedFile) {
      onError("Укажите название и выберите файл");
      return;
    }

    try {
      await upload(title.trim(), selectedFile);
      reset();
      onUploaded();
    } catch (error) {
      onError(error instanceof Error ? error.message : "Не удалось загрузить файл");
    }
  };

  return (
    <Modal show={show} onHide={handleClose} centered>
      <Form onSubmit={handleSubmit}>
        <Modal.Header closeButton>
          <Modal.Title>Добавить файл</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Form.Group className="mb-3">
            <Form.Label>Название</Form.Label>
            <Form.Control
              value={title}
              onChange={(event) => setTitle(event.target.value)}
              placeholder="Например, Договор с подрядчиком"
            />
          </Form.Group>
          <Form.Group>
            <Form.Label>Файл</Form.Label>
            <Form.Control
              type="file"
              onChange={(event) =>
                setSelectedFile((event.target as HTMLInputElement).files?.[0] ?? null)
              }
            />
          </Form.Group>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="outline-secondary" onClick={handleClose} disabled={isSubmitting}>
            Отмена
          </Button>
          <Button type="submit" variant="primary" disabled={isSubmitting}>
            {isSubmitting ? "Загрузка..." : "Сохранить"}
          </Button>
        </Modal.Footer>
      </Form>
    </Modal>
  );
}
