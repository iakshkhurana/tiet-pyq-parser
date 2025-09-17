export async function runPythonScript(option: string, value: string, mergePdfs: boolean, examFilter: string) {
  const res = await fetch('http://localhost:8000/run-script', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ option, value, mergePdfs, examFilter }),
  });
  return await res.json();
}
