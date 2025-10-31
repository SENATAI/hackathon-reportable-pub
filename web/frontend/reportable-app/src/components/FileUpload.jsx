import { useState } from "react";
import { motion } from "framer-motion";
import { Upload } from "lucide-react";
import "../styles/index.pcss";

export default function FileUpload({ onSubmit, loading }) {
  const [file, setFile] = useState(null);
  const [dragActive, setDragActive] = useState(false);

  const handleChange = (e) => setFile(e.target.files[0]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!file) return alert("Выберите файл");
    onSubmit(file);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setFile(e.dataTransfer.files[0]);
    }
  };

  return (
    <motion.form
      onSubmit={handleSubmit}
      className="file-upload"
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
    >
      <label
        className={`file-label ${dragActive ? "drag-active" : ""}`}
      >
        <Upload className="upload-icon" />
        <span>
          {file
            ? file.name
            : dragActive
            ? "Отпустите файл, чтобы загрузить"
            : "Перетащите или выберите файл"}
        </span>
        <input type="file" onChange={handleChange} className="hidden-input" />
      </label>

      <button
        type="submit"
        disabled={loading}
        className="upload-button"
      >
        {loading ? "Загрузка..." : "Отправить"}
      </button>
    </motion.form>
  );
}
