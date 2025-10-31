import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { analyzerApi } from "../api/analyzerApi";
import ResultTable from "../components/ResultTable";
import { motion } from "framer-motion";
import "../styles/index.pcss";

export default function ResultPage() {
  const { id } = useParams();
  const navigate = useNavigate();

  const [data, setData] = useState(null);
  const [error, setError] = useState(false);
  const [loading, setLoading] = useState(true);
  const [fileLoading, setFileLoading] = useState(false);

  useEffect(() => {
    const loadData = async () => {
      try {
        const res = await analyzerApi.getResult(id);
        if (res.error_type) setError(true);
        else setData(res);
      } catch {
        setError(true);
      } finally {
        setLoading(false);
      }
    };
    loadData();
  }, [id]);

  const handleOpenFile = async () => {
    if (!data?.input_file_id) return;
    try {
      setFileLoading(true);
      const fileData = await analyzerApi.getFileById(data.input_file_id);
      if (fileData?.url) {
        window.open(fileData.url, "_blank");
      } else {
        alert("Не удалось получить ссылку на файл");
      }
    } catch (err) {
      console.error(err);
      alert("Ошибка при получении файла");
    } finally {
      setFileLoading(false);
    }
  };

  const handleDownloadFile = async () => {
    if (!data?.input_file_id) return;
    try {
        setFileLoading(true);
        const fileData = await analyzerApi.getFileById(data.input_file_id);
        if (fileData?.url) {
        const link = document.createElement("a");
        link.href = fileData.url;
        link.download = fileData.filename || "file";
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        } else {
        alert("Не удалось получить ссылку на файл");
        }
    } catch (err) {
        console.error(err);
        alert("Ошибка при загрузке файла");
    } finally {
        setFileLoading(false);
    }
    };


  const handleDownloadJSON = () => {
    if (!data?.result_table) return;
    const blob = new Blob([JSON.stringify(data.result_table, null, 2)], {
      type: "application/json",
    });
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = `result-${id}.json`;
    link.click();
    URL.revokeObjectURL(link.href);
  };

  const handleGoHome = () => navigate("/");

  if (loading)
    return <div className="center-message">Загрузка...</div>;

  if (error)
    return (
      <motion.div className="center-message error" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
        ❌ Результат не найден
      </motion.div>
    );

  return (
    <motion.div className="result-container" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
      <h2 className="result-title">Результат анализа</h2>
      <p className="result-id">ID: {data.id}</p>

      <div className="button-row">
        <button
            className="action-button action-green"
            onClick={handleOpenFile}
            disabled={fileLoading}
        >
            {fileLoading ? "Загрузка файла..." : "Посмотреть исходный файл"}
        </button>

        <button
            className="action-button action-blue"
            onClick={handleDownloadJSON}
        >
            Скачать JSON
        </button>

        <button
            className="action-button action-gray"
            onClick={handleGoHome}
        >
            На главную
        </button>
        </div>


      <ResultTable data={data} />
    </motion.div>
  );
}
