import axios from "axios";

{
  const apiClient = axios.create({
    baseURL: "https://some-domain.com/api/",
  });
}

export default apiClient;