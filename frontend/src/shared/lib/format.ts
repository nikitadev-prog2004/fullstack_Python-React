const dateFormatter = new Intl.DateTimeFormat("ru-RU", {
  dateStyle: "short",
  timeStyle: "short",
});

export function formatDate(value: string): string {
  return dateFormatter.format(new Date(value));
}

const KB = 1024;
const MB = KB * 1024;

export function formatSize(size: number): string {
  if (size < KB) {
    return `${size} B`;
  }
  if (size < MB) {
    return `${(size / KB).toFixed(1)} KB`;
  }
  return `${(size / MB).toFixed(1)} MB`;
}
