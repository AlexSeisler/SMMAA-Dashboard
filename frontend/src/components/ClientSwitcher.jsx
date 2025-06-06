// frontend/src/components/ClientSwitcher.jsx
import React from "react";
const clients = [
  { id: "redrose_001", name: "Red Rose Media" },
  { id: "columbia_001", name: "Columbia Borough" }
];

const ClientSwitcher = ({ clientId, setClientId }) => {
  return (
    <div className="flex items-center gap-3">
      <label className="text-sm font-medium">Client:</label>
      <select
        value={clientId}
        onChange={(e) => setClientId(e.target.value)}
        className="border rounded-md px-2 py-1"
      >
        {clients.map((client) => (
          <option key={client.id} value={client.id}>
            {client.name}
          </option>
        ))}
      </select>
    </div>
  );
};

export default ClientSwitcher;
