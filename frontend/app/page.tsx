"use client"

import Image from "next/image"
import { useState } from "react";
import { runPythonScript } from "./api";

export default function App(){
  const [option, setOption] = useState("1");
  const [value, setValue] = useState("");
  const [mergePdfs, setMergePdfs] = useState(false);
  const [examFilter, setExamFilter] = useState("all");
  const [output, setOutput] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setOutput("");
    try {
      const res = await runPythonScript(option, value, mergePdfs, examFilter);
      if (res.output && res.output.includes("SUCCESS:")) {
        setOutput("✅ Papers downloaded to your Downloads/ThaparPapers folder");
      } else if (res.output && res.output.includes("No results found")) {
        setOutput("❌ No papers found for the given search criteria");
      } else {
        setOutput(res.error || "An error occurred");
      }
    } catch (error) {
      setOutput("❌ An error occurred while processing your request");
    }
    setLoading(false);
  }

  return <div className="app-container">
    <Image alt="logo" src="/thapar.jpeg" width={64} height={64} className="logo" />
    <form onSubmit={handleSubmit}>
      <div>
        <label>
          Option:
          <select value={option} onChange={e => setOption(e.target.value)}>
            <option value="1">Course Code</option>
            <option value="2">Course Name</option>
          </select>
        </label>
        <input
          type="text"
          placeholder={option === "1" ? "Enter Course Code" : "Enter Course Name"}
          value={value}
          onChange={e => setValue(e.target.value)}
        />
      </div>
      
      <div>
        <label>
          Exam Type Filter:
          <select value={examFilter} onChange={e => setExamFilter(e.target.value)}>
            <option value="all">All Types</option>
            <option value="MST">MST Only</option>
            <option value="EST">EST Only</option>
            <option value="AUX">AUX Only</option>
          </select>
        </label>
        
        <label>
          <input
            type="checkbox"
            checked={mergePdfs}
            onChange={e => setMergePdfs(e.target.checked)}
          />
          Merge PDFs into single file
        </label>
      </div>
      
      <button type="submit">Submit</button>
    </form>
    {loading && <div className="mt-4">Processing, Please wait...</div>}
    {output && <div className="mt-4"><pre>{output}</pre></div>}
  </div>
}