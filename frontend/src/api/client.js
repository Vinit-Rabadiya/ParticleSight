import axios from "axios";

// In development: uses localhost:8000
// In production (Vercel): VITE_API_URL is set to the Render backend URL
const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://localhost:8000",
});

export default apiClient;
