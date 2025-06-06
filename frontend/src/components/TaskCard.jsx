// frontend/src/components/TaskCard.jsx
import React from "react";
import StatusBadge from "./StatusBadge";

const TaskCard = ({ task }) => {
  return (
    <div className="rounded-2xl border p-4 shadow-sm bg-white space-y-2">
      <div className="flex justify-between items-center">
        <h2 className="font-semibold text-lg">{task.task}</h2>
        <StatusBadge status={task.status} />
      </div>

      <div className="text-sm text-gray-600">
        <span className="mr-2">Priority: {task.priority}</span>
        {task.due && <span>Due: {new Date(task.due).toLocaleDateString()}</span>}
      </div>

      <div className="text-xs text-gray-400">
        Source: {task.created_by || "unknown"}
      </div>
    </div>
  );
};

export default TaskCard;
