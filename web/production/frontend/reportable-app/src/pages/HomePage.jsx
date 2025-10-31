import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { analyzerApi } from "../api/analyzerApi";
import FileUpload from "../components/FileUpload";
import { motion } from "framer-motion";
import "../styles/index.pcss";

export default function HomePage() {
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleUpload = async (file) => {
    try {
      setLoading(true);
      const res = await analyzerApi.analyzeFile(file);
      if (res.id) navigate(`/result/${res.id}`);
      else alert("Ошибка обработки файла");
    } catch (e) {
      console.error(e);
      alert("Ошибка соединения с сервером");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page-container">
      <motion.h1
        className="main-title"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
      >
        👋 Добро пожаловать в Анализатор
      </motion.h1>
      <FileUpload onSubmit={handleUpload} loading={loading} />
    </div>
  );
}
