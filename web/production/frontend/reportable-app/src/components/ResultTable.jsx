import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import "../styles/ResultTable.pcss";

export default function ResultTable({ data }) {
  if (!data?.result_table) return null;

  const entries = Object.entries(data.result_table);

  return (
    <div className="result-tables">
      {entries.map(([date, tableData]) => (
        <DateSection key={date} date={date} tableData={tableData} />
      ))}
    </div>
  );
}

function DateSection({ date, tableData }) {
  const [open, setOpen] = useState(false);

  return (
    <div className="date-section">
      <div className="date-header" onClick={() => setOpen(!open)}>
        <h3>{date}</h3>
        <span className="toggle">{open ? "▲" : "▼"}</span>
      </div>

      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.3 }}
            className="date-content"
          >
            <div className="table-scroll-area">
              <RenderTable data={tableData} />
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

function RenderTable({ data }) {
  const keys = Object.keys(data);

  return (
    <table className="result-table">
      <thead>
        <tr>
          {keys.map((key) => (
            <th key={key}>{key}</th>
          ))}
        </tr>
      </thead>
      <tbody>
        <tr>
          {keys.map((key) => (
            <td key={key}>{renderValue(data[key])}</td>
          ))}
        </tr>
      </tbody>
    </table>
  );
}

function renderValue(value) {
  if (typeof value === "object" && !Array.isArray(value)) {
    return (
      <div className="nested-object">
        {Object.entries(value).map(([subKey, subVal]) => (
          <div key={subKey} className="nested-section">
            <h4>{subKey}</h4>
            {Array.isArray(subVal) && subVal.length > 0 ? (
              <div className="table-scroll-area">
                <table className="subtable">
                  <thead>
                    <tr>
                      {Object.keys(subVal[0]).map((k) => (
                        <th key={k}>{k}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {subVal.map((row, idx) => (
                      <tr key={idx}>
                        {Object.values(row).map((v, i) => (
                          <td key={i}>
                            {typeof v === "object"
                              ? JSON.stringify(v)
                              : v ?? "—"}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <p className="empty">—</p>
            )}
          </div>
        ))}
      </div>
    );
  }

  if (Array.isArray(value)) {
    if (value.length === 0) return "—";
    if (typeof value[0] === "object") {
      return (
        <div className="table-scroll-area">
          <table className="subtable">
            <thead>
              <tr>
                {Object.keys(value[0]).map((k) => (
                  <th key={k}>{k}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {value.map((row, i) => (
                <tr key={i}>
                  {Object.values(row).map((v, j) => (
                    <td key={j}>
                      {typeof v === "object" ? JSON.stringify(v) : v ?? "—"}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      );
    } else {
      return value.join(", ");
    }
  }

  // 🩹 исправление тут:
  if (
    typeof value === "string" ||
    typeof value === "number" ||
    typeof value === "boolean"
  ) {
    return String(value);
  }

  if (value == null) return "—";

  // Если объект или что-то непонятное — безопасно преобразуем
  try {
    return JSON.stringify(value);
  } catch {
    return String(value);
  }
}

