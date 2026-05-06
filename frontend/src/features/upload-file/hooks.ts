"use client";

import { useCallback, useState } from "react";
import { uploadFileApi } from "./api";

export function useUploadFile() {
  const [isSubmitting, setIsSubmitting] = useState(false);

  const upload = useCallback(async (title: string, file: File): Promise<void> => {
    setIsSubmitting(true);
    try {
      await uploadFileApi.upload(title, file);
    } finally {
      setIsSubmitting(false);
    }
  }, []);

  return { upload, isSubmitting };
}
