export function PriorityBadge({ priority }) {
  if (!priority) return null
  return <span className={`badge badge-${priority}`}>{priority}</span>
}

export function StatusBadge({ status }) {
  if (!status) return null
  return <span className="badge badge-status">{status.replace('_', ' ')}</span>
}
