import React, { useEffect, useState } from "react";
import axios from "axios";
import { API_BASE_URL } from "../config";
const Profile = () => {
  const [user, setUser] = useState(null);

  useEffect(() => {
    const token = localStorage.getItem("token");

    axios
      .get(`${API_BASE_URL}/profile`, {
        headers: { Authorization: token },
      })
      .then((res) => setUser(res.data.user))
      .catch(() => setUser(null));
  }, []);

  if (!user) return <p>Loading or unauthorized...</p>;

  return (
    <div>
      <h2>Welcome, {user.name}</h2>
      <p>Email: {user.email}</p>
    </div>
  )
}

export default Profile