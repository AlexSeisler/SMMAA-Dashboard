// frontend/src/pages/Dashboard.jsx
import React from "react";
import { useEffect, useState } from "react";
import { supabase } from "../lib/supabaseClient";
import TaskCard from "../components/TaskCard";
import ClientSwitcher from "../components/ClientSwitcher";

const Dashboard = () => {
  const [tasks, setTasks] = useState([]);
  const [clientId, setClientId] = useState("redrose_001"); // default for now

  useEffect(() => {
    fetchTasks(clientId);
  }, [clientId]);

  const fetchTasks = async (client_id) => {
    const { data, error } = await supabase
      .from("tasks")
      .select("*")
      .eq("client_id", client_id)
      .order("inserted_at", { ascending: false });

    if (error) {
      console.error("Error fetching tasks:", error.message);
    } else {
      setTasks(data);
    }
  };

  return (
    <div className="p-6 space-y-4">
      <h1 className="text-2xl font-bold">Task Tracker</h1>

      <ClientSwitcher clientId={clientId} setClientId={setClientId} />

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {tasks.map((task) => (
          <TaskCard key={task.id} task={task} />
        ))}
      </div>
    </div>
  );
};

export default Dashboard;
