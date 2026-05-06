import { apiClient, buildUrl } from "../../shared/api/client";
import { FileItem } from "./types";

export const filesApi = {
  list: () => apiClient.get<FileItem[]>("/files"),
  downloadUrl: (id: string) => buildUrl(`/files/${id}/download`),
};
