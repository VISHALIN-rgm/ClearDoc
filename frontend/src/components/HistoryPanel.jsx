const STATUS_LABEL = {
  complete: 'Ready',
  processing: 'Processing',
  failed: 'Failed',
  cancelled: 'Cancelled',
}

export default function HistoryPanel({ open, onClose, items, loading, onOpen, onDelete }) {
  if (!open) return null

  return (
    <div className="history-overlay" onClick={onClose}>
      <div className="glass-card history-panel" onClick={(e) => e.stopPropagation()}>
        <div className="history-header">
          <h3>Recent documents</h3>
          <button className="ghost-button history-close" onClick={onClose} aria-label="Close">
            <CloseIcon />
          </button>
        </div>

        {loading && items.length === 0 && <p className="fine-print">Loading…</p>}
        {!loading && items.length === 0 && (
          <p className="fine-print">Documents you analyze will show up here.</p>
        )}

        <ul className="history-items">
          {items.map((item) => {
            const openable = item.status === 'complete'
            return (
              <li key={item.documentId} className="history-item">
                <button
                  className="history-open-btn"
                  onClick={() => openable && onOpen(item)}
                  disabled={!openable}
                  aria-label={openable ? `Open ${item.documentName || 'document'}` : undefined}
                >
                  <div>
                    <p className="history-name">{item.documentName || 'Document'}</p>
                    <span className={`status-chip status-${item.status}`}>
                      {STATUS_LABEL[item.status] || item.status}
                    </span>
                  </div>
                </button>
                <button
                  className="history-delete-btn"
                  onClick={() => onDelete(item.documentId)}
                  aria-label={`Delete ${item.documentName || 'document'}`}
                >
                  <TrashIcon />
                </button>
              </li>
            )
          })}
        </ul>
      </div>
    </div>
  )
}

function CloseIcon() {
  return (
    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2">
      <path d="M6 6l12 12M18 6L6 18" strokeLinecap="round" />
    </svg>
  )
}

function TrashIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
      <path d="M4 7h16" strokeLinecap="round" />
      <path d="M9 7V4.5A1.5 1.5 0 0 1 10.5 3h3A1.5 1.5 0 0 1 15 4.5V7" strokeLinecap="round" strokeLinejoin="round" />
      <path d="M18 7l-.8 12.4A2 2 0 0 1 15.2 21H8.8a2 2 0 0 1-2-1.6L6 7" strokeLinecap="round" strokeLinejoin="round" />
      <path d="M10 11v6M14 11v6" strokeLinecap="round" />
    </svg>
  )
}
