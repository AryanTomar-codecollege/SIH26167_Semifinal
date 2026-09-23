const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000"

export async function submitQuery({ files, query, taskHint = "auto" }) {
  const form = new FormData()
  files.forEach(({ file }) => {
    if (file) form.append("files", file, file.name)
  })
  form.append("query", query)
  form.append("task_hint", taskHint)

  const response = await fetch(`${API_BASE}/api/query`, {
    method: "POST",
    body: form,
  })

  const data = await response.json().catch(() => null)
  if (!response.ok || data?.success === false) {
    throw new Error(data?.error || `Request failed with ${response.status}`)
  }
  return data
}

export async function healthCheck() {
  const response = await fetch(`${API_BASE}/`)
  return response.ok
}
