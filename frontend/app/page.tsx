"use client"

import Image from "next/image"
import { useState } from "react";
import { runPythonScript } from "./api";
import { LoadingButton } from "@/components/loading-button";
import { WordPullUp } from "@/components/ui/word-pull-up";

export default function App(){
  const [option, setOption] = useState("1");
  const [value, setValue] = useState("");
  const [mergePdfs, setMergePdfs] = useState(false);
  const [examFilter, setExamFilter] = useState("all");
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setSuccess(false);
    setError("");
    
    try {
      const res = await runPythonScript(option, value, mergePdfs, examFilter);
      if (res.output && res.output.includes("SUCCESS:")) {
        setSuccess(true);
        setLoading(false);
        // Reset success after 3 seconds
        setTimeout(() => setSuccess(false), 3000);
      } else if (res.output && res.output.includes("No results found")) {
        setError("❌ No papers found for the given search criteria");
        setLoading(false);
      } else {
        setError(res.error || "An error occurred");
        setLoading(false);
      }
    } catch (error) {
      setError("❌ An error occurred while processing your request");
      setLoading(false);
    }
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
      
      <LoadingButton 
        type="submit" 
        loading={loading}
        className="w-full"
      >
        {loading ? "Parsing..." : "Submit"}
      </LoadingButton>
    </form>
    
    {success && (
      <div className="mt-6 flex justify-center">
        <WordPullUp 
          words="Successfully Downloaded" 
          className="text-green-600 text-2xl"
        />
      </div>
    )}
    
    {error && (
      <div className="mt-4 text-center text-red-600">
        {error}
      </div>
    )}
  </div>
}