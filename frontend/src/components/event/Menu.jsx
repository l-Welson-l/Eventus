import { useState, useEffect } from "react";
import { Document, Page, pdfjs } from "react-pdf";
import "react-pdf/dist/esm/Page/AnnotationLayer.css";

pdfjs.GlobalWorkerOptions.workerSrc = `//cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjs.version}/pdf.worker.min.js`;

export default function Menu({ event }) {
  const [open, setOpen] = useState(false);
  const [numPages, setNumPages] = useState(null);
  const [pageNumber, setPageNumber] = useState(1);
  const [width, setWidth] = useState(Math.min(window.innerWidth * 0.9, 600));
  const [touchStart, setTouchStart] = useState(null);

  // Resize listener for responsiveness
  useEffect(() => {
    const handleResize = () =>
      setWidth(Math.min(window.innerWidth * 0.9, 600));
    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, []);

  if (!event || !event.menu_file) return null;

  const menuUrl =
    event.menu_file.startsWith("http")
      ? event.menu_file
      : `http://localhost:8000${event.menu_file}`;

  const onDocumentLoadSuccess = ({ numPages }) => {
    setNumPages(numPages);
    setPageNumber(1);
  };

  const prevPage = () => setPageNumber((p) => Math.max(1, p - 1));
  const nextPage = () => setPageNumber((p) => Math.min(numPages, p + 1));

  // Swipe handlers
  const handleTouchStart = (e) => setTouchStart(e.touches[0].clientX);
  const handleTouchEnd = (e) => {
    if (touchStart === null) return;
    const touchEnd = e.changedTouches[0].clientX;
    const diff = touchStart - touchEnd;
    if (diff > 50) nextPage(); // swipe left → next
    else if (diff < -50) prevPage(); // swipe right → prev
    setTouchStart(null);
  };

  return (
    <>
      <button onClick={() => setOpen(true)} style={styles.button}>
        View Menu
      </button>

      {open && (
        <div style={styles.overlay} onClick={() => setOpen(false)}>
          <div
            style={styles.modal}
            onClick={(e) => e.stopPropagation()}
            onTouchStart={handleTouchStart}
            onTouchEnd={handleTouchEnd}
          >
            <button style={styles.close} onClick={() => setOpen(false)}>
              ✕
            </button>

            <Document
              file={menuUrl}
              onLoadSuccess={onDocumentLoadSuccess}
              loading="Loading PDF..."
            >
              <Page
                pageNumber={pageNumber}
                width={width}
                renderAnnotationLayer={false}
                renderTextLayer={false}
              />
            </Document>

            {numPages > 1 && (
              <div style={styles.navContainer}>
                <button onClick={prevPage} style={styles.navBtn}>
                  ‹
                </button>
                <p style={{ margin: "0 10px" }}>
                  {pageNumber} / {numPages}
                </p>
                <button onClick={nextPage} style={styles.navBtn}>
                  ›
                </button>
              </div>
            )}
          </div>
        </div>
      )}
    </>
  );
}

const styles = {
  button: {
    padding: "8px 12px",
    borderRadius: 6,
    background: "#1a73e8",
    color: "#fff",
    border: "none",
    cursor: "pointer",
  },
  overlay: {
    position: "fixed",
    inset: 0,
    background: "rgba(0,0,0,0.9)",
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
    zIndex: 1000,
    overflowY: "auto",
    padding: 20,
  },
  modal: {
    position: "relative",
    maxWidth: 600,
    width: "100%",
    background: "#fff",
    padding: 10,
    borderRadius: 10,
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
  },
  close: {
    position: "absolute",
    top: 10,
    right: 10,
    background: "red",
    color: "#fff",
    border: "none",
    borderRadius: 6,
    padding: "4px 8px",
    cursor: "pointer",
  },
  navContainer: {
    display: "flex",
    alignItems: "center",
    marginTop: 10,
  },
  navBtn: {
    padding: "6px 12px",
    fontSize: 20,
    background: "#1a73e8",
    color: "#fff",
    border: "none",
    borderRadius: 6,
    cursor: "pointer",
  },
};
