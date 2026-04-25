type StatusBadgeProps = {
  status: string;
};

export function StatusBadge({ status }: StatusBadgeProps) {
  const normalized = status.toLowerCase();
  const className = `status-badge status-${normalized}`;

  return <span className={className}>{normalized}</span>;
}
