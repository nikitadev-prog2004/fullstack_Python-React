import { apiClient } from "../../shared/api/client";
import { AlertItem } from "./types";

export const alertsApi = {
  list: () => apiClient.get<AlertItem[]>("/alerts"),
};
