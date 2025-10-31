import axios from "axios";

export const analyzerApi = {
  analyzeFile: async (file) => {
    const formData = new FormData();
    formData.append("file", file);
    const { data } = await axios.post(
      `/api/analyzer/analyze/`, 
      formData, 
      {
        headers: { "Content-Type": "multipart/form-data" },
        timeout: 300000, // 5 минут (300000 мс)
      }
    );
    return data;
  },

  getResult: async (id) => {
    const { data } = await axios.get(`/api/analyzer/${id}`);
    return data;
  },

  // 🔥 Новый метод
  getFileById: async (fileId) => {
    const { data } = await axios.get(`/api/files/${fileId}`);
    return data;
  },
};

