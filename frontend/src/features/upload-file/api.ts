import { apiClient } from "../../shared/api/client";
import { FileItem } from "../../entities/file/types";

export const uploadFileApi = {
  upload: (title: string, file: File) => {
    const formData = new FormData();
    formData.append("title", title);
    formData.append("file", file);
    return apiClient.post<FileItem>("/files", { body: formData });
  },
};
