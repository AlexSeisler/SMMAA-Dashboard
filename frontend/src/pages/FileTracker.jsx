// frontend/src/pages/FileTracker.jsx
import React from "react";
import { useEffect, useState } from "react";
import { supabase } from "../lib/supabaseClient";
import FileCard from "../components/FileCard";
import ClientSwitcher from "../components/ClientSwitcher";

const FileTracker = () => {
  const [files, setFiles] = useState([]);
  const [clientId, setClientId] = useState("redrose_001");

  useEffect(() => {
    fetchFiles(clientId);
  }, [clientId]);

  const fetchFiles = async (client_id) => {
    const { data, error } = await supabase
      .from("files")
      .select("*")
      .eq("client_id", client_id)
      .order("inserted_at", { ascending: false });

    if (error) console.error("File fetch error:", error.message);
    else setFiles(data);
  };

  return (
    <div className="p-6 space-y-4">
      <h1 className="text-2xl font-bold">File Tracker</h1>
      <ClientSwitcher clientId={clientId} setClientId={setClientId} />

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 pt-4">
        {files.map((file) => (
          <FileCard key={file.id} file={file} />
        ))}
      </div>
    </div>
  );
};

export default FileTracker;
