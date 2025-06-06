// frontend/src/components/StatusBadge.jsx
import React from "react";
const badgeColors = {
  to_do: "bg-gray-200 text-gray-800",
  in_progress: "bg-yellow-200 text-yellow-800",
  done: "bg-green-200 text-green-800",
  uploaded: "bg-blue-200 text-blue-800"
};

const StatusBadge = ({ status }) => {
  const style = badgeColors[status] || "bg-gray-100 text-gray-700";
  return (
    <span className={`px-2 py-1 rounded-full text-xs font-medium ${style}`}>
      {status.replaceAll("_", " ")}
    </span>
  );
};

export default StatusBadge;
