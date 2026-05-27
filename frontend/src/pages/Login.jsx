import React, {useState} from 'react'

import { useNavigate } from "react-router-dom";
import { useAuth } from '../context/AuthContext';
import { LogIn, Loader2 } from 'lucide-react';
import { API_BASE_URL } from "../config";
const Login = () => {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [form, setForm] = useState({ email: "", password: "" });
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE_URL}/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(form),
      });
      const data = await res.json();
      if (res.ok) {
        login(data);
        navigate("/");
      } else {
        alert(data.error || "Login failed");
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <form onSubmit={handleSubmit} className="bg-white p-8 shadow-lg rounded-2xl w-96">
        <h2 className="text-2xl font-bold mb-6 text-center">Login</h2>
        <input name="email" type="email" placeholder="Email" onChange={handleChange}
          className="w-full border p-2 mb-3 rounded" required />
        <input name="password" type="password" placeholder="Password" onChange={handleChange}
          className="w-full border p-2 mb-3 rounded" required />
        <button disabled={loading}
          className="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700 inline-flex items-center justify-center gap-2 disabled:opacity-50">
          {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <LogIn className="h-4 w-4" />}
          <span>{loading ? "Logging in..." : "Login"}</span>
        </button>
        <p className="text-sm text-gray-500 mt-4 text-center">
          Don’t have an account?{" "}
          <span onClick={() => navigate("/signup")} className="text-blue-600 cursor-pointer">
            Sign up
          </span>
        </p>
      </form>
    </div>
  )
}

export default Login
