// Strip any trailing slash so `${BASE_URL}/upload` never produces a
// double slash — protects against a trailing slash accidentally left
// in VITE_API_BASE_URL. Defaults to the local FastAPI dev server.
const BASE_URL = (import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000').replace(/\/+$/, '')

function fileToBase64(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = () => resolve(reader.result.split(',')[1])
    reader.onerror = reject
    reader.readAsDataURL(file)
  })
}

export async function uploadDocument(file) {
  const base64 = await fileToBase64(file)
  const response = await fetch(`${BASE_URL}/upload`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ file: base64, file_name: file.name }),
  })
  if (!response.ok) {
    throw new Error(`Upload failed: ${response.status}`)
  }
  return response.json() // { documentId, status }
}

export async function getResult(documentId) {
  const response = await fetch(`${BASE_URL}/result/${documentId}`)
  if (!response.ok) {
    throw new Error(`Fetch failed: ${response.status}`)
  }
  return response.json()
}

export async function listResults() {
  const response = await fetch(`${BASE_URL}/results`)
  if (!response.ok) {
    throw new Error(`Fetch failed: ${response.status}`)
  }
  return response.json()
}

/**
 * Deletes a document's result, uploaded file, and audio narration.
 * Also flags any in-flight job for that id so a pipeline that's
 * mid-run can't resurrect it after this returns.
 */
export async function deleteDocument(documentId) {
  const response = await fetch(`${BASE_URL}/result/${documentId}`, { method: 'DELETE' })
  if (!response.ok) {
    throw new Error(`Delete failed: ${response.status}`)
  }
  return response.json()
}

/**
 * Best-effort cancel of an in-flight job. Never throws — the caller
 * should already be treating cancel as instant on the frontend side
 * (see pollResult's shouldStop), so a network hiccup here shouldn't
 * block the UI from returning to the upload screen.
 */
export async function cancelDocument(documentId) {
  try {
    const response = await fetch(`${BASE_URL}/cancel/${documentId}`, { method: 'POST' })
    if (!response.ok) return null
    return await response.json()
  } catch {
    return null
  }
}

export async function getChatHistory(documentId) {
  const response = await fetch(`${BASE_URL}/chat/${documentId}`)
  if (!response.ok) {
    throw new Error(`Fetch failed: ${response.status}`)
  }
  return response.json() // { documentId, history }
}

export async function sendChatMessage(documentId, message) {
  const response = await fetch(`${BASE_URL}/chat/${documentId}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message }),
  })
  if (!response.ok) {
    const body = await response.json().catch(() => ({}))
    throw new Error(body.detail || `Chat failed: ${response.status}`)
  }
  return response.json() // { documentId, reply, history }
}

/**
 * Polls GET /result/{documentId} until status is "complete", "failed",
 * or "cancelled". Pass `shouldStop` to make cancellation immediate on
 * the frontend side — it's checked before every poll, so the caller
 * doesn't have to wait for the next network round-trip once the user
 * cancels.
 */
export async function pollResult(documentId, { intervalMs = 2500, timeoutMs = 90000, shouldStop } = {}) {
  const start = Date.now()
  while (Date.now() - start < timeoutMs) {
    if (shouldStop && shouldStop()) {
      return { documentId, status: 'cancelled' }
    }
    const result = await getResult(documentId)
    if (result.status === 'complete' || result.status === 'failed' || result.status === 'cancelled') {
      return result
    }
    await new Promise((r) => setTimeout(r, intervalMs))
  }
  throw new Error('Timed out waiting for analysis to finish.')
}
