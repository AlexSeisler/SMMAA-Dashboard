// frontend/src/components/FileCard.jsx

import StatusBadge from "./StatusBadge";

const FileCard = ({ file }) => {
  return (
    <div className="p-3 rounded-xl border bg-white shadow-sm">
      <div className="font-medium">{file.file_url.split("/").pop()}</div>
      <div className="flex justify-between text-sm text-gray-500 mt-1">
        <span>Task ID: {file.task_id}</span>
        <StatusBadge status={file.status} />
      </div>
    </div>
  );
};

export default FileCard;
