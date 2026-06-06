(function () {
  const { useEffect, useMemo, useRef, useState } = React;

  const modules = [
    { id: "home", label: "Home", icon: "/assets/ui_icons/home.png" },
    { id: "upload", label: "Upload", icon: "/assets/ui_icons/upload.png" },
    { id: "preprocess", label: "Preprocessing", icon: "/assets/ui_icons/preprocessing.png" },
    { id: "ocr", label: "OCR", icon: "/assets/ui_icons/ocr.png" },
    { id: "medicines", label: "Medicines", icon: "/assets/ui_icons/medicines.png" },
    { id: "dosage", label: "Dosage", icon: "/assets/ui_icons/dosage.png" },
    { id: "benefits", label: "Benefits", icon: "/assets/ui_icons/benefits.png" },
    { id: "interactions", label: "Interactions", icon: "/assets/ui_icons/interactions.png" },
    { id: "recommendations", label: "Recommendations", icon: "/assets/ui_icons/recommendations.png" },
    { id: "dashboard", label: "Dashboard", icon: "/assets/ui_icons/dashboard.png" },
    { id: "database", label: "Database", icon: "/assets/ui_icons/database.png" },
  ];

  const h = React.createElement;

  function api(path, options) {
    return fetch(path, options).then(async (response) => {
      const data = await response.json().catch(() => ({}));
      if (!response.ok) {
        throw new Error(data.detail || data.message || "Request failed");
      }
      return data;
    });
  }

  function Status({ message, error }) {
    if (!message) return null;
    return h("div", { className: `status${error ? " error" : ""}` }, message);
  }

  function ModuleNav({ active, setActive }) {
    return h(
      "nav",
      { className: "top-nav-button-panel", "aria-label": "Main navigation" },
      h(
        "div",
        { className: "top-nav-button-row" },
        modules.map((item) =>
          h(
            "button",
            {
              key: item.id,
              className: `top-nav-button${active === item.id ? " active" : ""}`,
              onClick: () => setActive(item.id),
              title: item.label,
            },
            h("span", null, h("img", { className: "nav-option-logo", src: item.icon, alt: "" }), item.label)
          )
        )
      )
    );
  }

  function Topbar({ user, onLogin, onLogout }) {
    return h(
      "header",
      { className: "top-nav-bar" },
      h(
        "div",
        { className: "nav-header" },
        h(
          "div",
          { className: "nav-brand" },
          h("img", { className: "nav-logo", src: "/assets/ai_prescription_logo.png", alt: "AI Prescription Reader logo" }),
          h(
            "div",
            null,
            h("div", { className: "nav-title" }, "AI Prescription Reader"),
            h("div", { className: "nav-subtitle" }, "Advanced Medicine Intelligence & Analysis Platform")
          )
        ),
        h(
          "div",
          { className: "nav-user-status" },
          h("div", null, h("img", { className: "user-status-icon", src: "/assets/ui_icons/user.png", alt: "" }), h("strong", null, user || "Guest")),
          user
            ? h("button", { className: "nav-login-button", onClick: onLogout }, "Logout")
            : h("button", { className: "nav-login-button", onClick: onLogin }, "Login to save data under your name")
        )
      )
    );
  }

  function Home({ files, user, onLogin, onClearOutputs }) {
    const uploadCount = files.uploads.length;
    const preprocessedCount = files.preprocessed.length;
    const ocrCount = files.ocr.filter((file) => file.name.endsWith(".txt")).length;
    const medicineCount = files.medicines.filter((file) => file.name.endsWith(".json")).length;

    return h(
      React.Fragment,
      null,
      h(
        "div",
        { className: "account-row" },
        h("div", { className: "info-box" }, user ? `Signed in as ${user}.` : "Login to store prescriptions and reports under your name."),
        h("select", { className: "language-select", defaultValue: "English", title: "Language" }, h("option", null, "English"), h("option", null, "Hindi"), h("option", null, "Telugu")),
        h("button", { className: "secondary", onClick: onLogin }, user ? "Change User" : "Login"),
        h("button", { className: "danger", onClick: onClearOutputs }, "Clear All Output")
      ),
      h(
        "section",
        { className: "hero-section" },
        h("h1", { className: "hero-title" }, h("img", { className: "hero-title-logo", src: "/assets/ai_prescription_logo.png", alt: "" }), "Medicine Prescription Analysis Platform"),
        h("p", { className: "hero-subtitle" }, "Advanced AI-powered medicine intelligence and prescription analysis system")
      ),
      h(
        "section",
        { className: "workflow-stats two-stat-grid" },
        h("div", { className: "stat-box" }, h("p", { className: "stat-number" }, "24/7"), h("p", { className: "stat-label" }, "Database Access")),
        h("div", { className: "stat-box" }, h("p", { className: "stat-number" }, "MongoDB"), h("p", { className: "stat-label" }, "Cloud Storage"))
      ),
      h(
        "div",
        { className: "medical-disclaimer" },
        h("div", null, h("strong", null, "Medical Disclaimer"), h("p", null, "This AI Prescription Reader is designed to assist with prescription text extraction and medicine information only. It is not a substitute for professional medical advice, diagnosis, or treatment. Always confirm medicines, dosage, interactions, and recommendations with a licensed doctor or pharmacist before making health decisions."))
      ),
      h("div", { className: "section-divider" }),
      h(
        "section",
        { className: "panel" },
        h(
          "div",
          { className: "panel-header" },
          h("div", null, h("h3", null, "Workflow"), h("p", null, "Use the module rail to move through the same prescription pipeline."))
        ),
        h(
          "div",
          { className: "feature-grid" },
          h("div", { className: "feature-item" }, h("img", { className: "feature-icon", src: "/assets/ui_icons/preprocessing.png", alt: "" }), h("h3", { className: "feature-title" }, "Image Processing"), h("p", { className: "feature-text" }, "Advanced preprocessing and enhancement of prescription images")),
          h("div", { className: "feature-item" }, h("img", { className: "feature-icon", src: "/assets/ui_icons/ocr.png", alt: "" }), h("h3", { className: "feature-title" }, "OCR Technology"), h("p", { className: "feature-text" }, "Accurate text extraction using state-of-the-art OCR engines")),
          h("div", { className: "feature-item" }, h("img", { className: "feature-icon", src: "/assets/ui_icons/medicines.png", alt: "" }), h("h3", { className: "feature-title" }, "AI Analysis"), h("p", { className: "feature-text" }, "Intelligent medicine detection and interaction analysis"))
        )
      )
    );
  }

  function WorkspaceOverview({ active, files, setActive }) {
    if (active === "home") return null;
    const medicineCount = files.medicines.filter((file) => file.name.endsWith(".json")).length;
    const dosageCount = files.dosage.filter((file) => file.name.endsWith(".json")).length;
    const benefitsCount = files.benefits.filter((file) => file.name.endsWith(".json")).length;
    const completion = Math.round(((modules.findIndex((item) => item.id === active) + 1) / modules.length) * 100);
    return h(
      "section",
      { className: "workspace-overview" },
      h(
        "div",
        { className: "workspace-topline" },
        h("div", { className: "workspace-title" }, h("h1", null, "AI Prescription Reader & Medicine Intelligence System"), h("p", null, `Understand your prescription in a better way with AI. Current workspace: ${modules.find((item) => item.id === active)?.label || "Home"}`)),
        h("button", { className: "workspace-action", onClick: () => setActive("upload") }, "Upload New")
      ),
      h(
        "div",
        { className: "summary-card-grid" },
        h(SummaryCard, { icon: "/assets/ui_icons/medicines.png", label: "Medicines", value: medicineCount, caption: "Detected medicine rows" }),
        h(SummaryCard, { icon: "/assets/ui_icons/dosage.png", label: "Dosage", value: dosageCount, caption: "Dosage rows extracted" }),
        h(SummaryCard, { icon: "/assets/ui_icons/benefits.png", label: "Benefits", value: benefitsCount, caption: "Benefit files generated" }),
        h(SummaryCard, { icon: "/assets/ui_icons/interactions.png", label: "Interactions", value: 0, caption: "Warnings available" }),
        h(SummaryCard, { icon: "/assets/ui_icons/dashboard.png", label: "Completed", value: `${completion}%`, caption: "Current workflow position" })
      )
    );
  }

  function SummaryCard({ icon, label, value, caption }) {
    return h(
      "div",
      { className: "summary-card" },
      h("img", { src: icon, alt: "" }),
      h("div", null, h("p", { className: "summary-label" }, label), h("p", { className: "summary-value" }, value), h("p", { className: "summary-caption" }, caption))
    );
  }

  function StepControls({ active, setActive }) {
    const currentIndex = modules.findIndex((item) => item.id === active);
    if (currentIndex < 0) return null;

    const previous = modules[currentIndex - 1];
    const next = modules[currentIndex + 1];

    return h(
      "div",
      { className: "step-controls" },
      h(
        "button",
        {
          className: "secondary",
          disabled: !previous,
          onClick: () => previous && setActive(previous.id),
        },
        previous ? `Previous: ${previous.label}` : "Previous"
      ),
      h(
        "div",
        { className: "step-position" },
        `Step ${currentIndex + 1} of ${modules.length}`
      ),
      h(
        "button",
        {
          className: "primary",
          disabled: !next,
          onClick: () => next && setActive(next.id),
        },
        next ? `Next: ${next.label}` : "Next"
      )
    );
  }

  function Upload({ onRefresh }) {
    const [file, setFile] = useState(null);
    const [preview, setPreview] = useState("");
    const [status, setStatus] = useState("");
    const [error, setError] = useState("");
    const [busy, setBusy] = useState(false);

    useEffect(() => {
      if (!file) {
        setPreview("");
        return;
      }
      const url = URL.createObjectURL(file);
      setPreview(url);
      return () => URL.revokeObjectURL(url);
    }, [file]);

    async function submit(event) {
      event.preventDefault();
      if (!file) return;

      setBusy(true);
      setStatus("");
      setError("");

      const form = new FormData();
      form.append("file", file);

      try {
        const data = await api("/api/upload", { method: "POST", body: form });
        setStatus(`Saved ${data.file.saved_file_name}`);
        await onRefresh();
      } catch (err) {
        setError(err.message);
      } finally {
        setBusy(false);
      }
    }

    return h(
      "section",
      { className: "panel" },
      h(
        "div",
        { className: "panel-header" },
        h("div", null, h("h3", null, "Prescription Upload"), h("p", null, "Choose a clear prescription image and save it for preprocessing."))
      ),
      h(
        "form",
        { className: "grid-2", onSubmit: submit },
        h(
          "div",
          null,
          h("label", { className: "field" }, "Prescription image", h("input", { type: "file", accept: ".jpg,.jpeg,.png,image/*", onChange: (event) => setFile(event.target.files[0] || null) })),
          h("button", { className: "primary", disabled: !file || busy }, busy ? "Uploading..." : "Submit Prescription"),
          h(Status, { message: error || status, error: Boolean(error) })
        ),
        h("div", { className: "image-preview" }, preview ? h("img", { src: preview, alt: "Selected prescription preview" }) : "No image selected")
      )
    );
  }

  function Preprocess({ files, onRefresh }) {
    const [selected, setSelected] = useState("");
    const [options, setOptions] = useState({
      apply_gray: true,
      apply_noise: true,
      apply_contrast: true,
      apply_threshold: true,
      handwriting_enhancement: true,
    });
    const [result, setResult] = useState(null);
    const [status, setStatus] = useState("");
    const [error, setError] = useState("");
    const [busy, setBusy] = useState(false);

    useEffect(() => {
      if (!selected && files.uploads[0]) setSelected(files.uploads[0].path);
    }, [files.uploads, selected]);

    const selectedFile = files.uploads.find((file) => file.path === selected);

    function toggle(key) {
      setOptions((current) => ({ ...current, [key]: !current[key] }));
    }

    async function run() {
      if (!selected) return;
      setBusy(true);
      setStatus("");
      setError("");

      try {
        const data = await api("/api/preprocess", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ image_path: selected, ...options }),
        });
        setResult(data);
        setStatus("Preprocessed image saved.");
        await onRefresh();
      } catch (err) {
        setError(err.message);
      } finally {
        setBusy(false);
      }
    }

    return h(
      "section",
      { className: "panel" },
      h("div", { className: "panel-header" }, h("div", null, h("h3", null, "Image Preprocessing"), h("p", null, "Enhance the upload before OCR."))),
      h(
        "div",
        { className: "grid-2" },
        h(
          "div",
          null,
          h("label", { className: "field" }, "Uploaded image", h("select", { value: selected, onChange: (event) => setSelected(event.target.value) }, files.uploads.map((file) => h("option", { key: file.path, value: file.path }, file.name)))),
          h(
            "div",
            { className: "control-grid" },
            Object.keys(options).map((key) =>
              h("label", { className: "check", key }, h("input", { type: "checkbox", checked: options[key], onChange: () => toggle(key) }), key.replaceAll("_", " "))
            )
          ),
          h("button", { className: "primary", onClick: run, disabled: !selected || busy }, busy ? "Processing..." : "Preprocess Image"),
          h(Status, { message: error || status, error: Boolean(error) })
        ),
        h("div", { className: "image-preview" }, result ? h("img", { src: result.url, alt: "Preprocessed result" }) : selectedFile ? h("img", { src: selectedFile.url, alt: "Uploaded prescription" }) : "No upload available")
      )
    );
  }

  function OCR({ files, onRefresh, setOcrText }) {
    const [selected, setSelected] = useState("");
    const [engine, setEngine] = useState("Tesseract OCR");
    const [handwriting, setHandwriting] = useState(false);
    const [result, setResult] = useState(null);
    const [status, setStatus] = useState("");
    const [error, setError] = useState("");
    const [busy, setBusy] = useState(false);

    useEffect(() => {
      if (!selected && files.preprocessed[0]) setSelected(files.preprocessed[0].path);
    }, [files.preprocessed, selected]);

    const selectedFile = files.preprocessed.find((file) => file.path === selected);

    async function run() {
      if (!selected) return;
      setBusy(true);
      setStatus("");
      setError("");

      try {
        const data = await api("/api/ocr", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ image_path: selected, ocr_engine: engine, handwriting_mode: handwriting }),
        });
        setResult(data);
        setOcrText(data.combined_text || "");
        setStatus("OCR extraction completed.");
        await onRefresh();
      } catch (err) {
        setError(err.message);
      } finally {
        setBusy(false);
      }
    }

    return h(
      "section",
      { className: "panel" },
      h("div", { className: "panel-header" }, h("div", null, h("h3", null, "OCR Text Extraction"), h("p", null, "Uses module_05_ocr.py through the FastAPI backend."))),
      h(
        "div",
        { className: "grid-2" },
        h(
          "div",
          null,
          h("label", { className: "field" }, "Preprocessed image", h("select", { value: selected, onChange: (event) => setSelected(event.target.value) }, files.preprocessed.map((file) => h("option", { key: file.path, value: file.path }, file.name)))),
          h("label", { className: "field" }, "OCR engine", h("select", { value: engine, onChange: (event) => setEngine(event.target.value) }, ["Tesseract OCR", "EasyOCR", "Both"].map((item) => h("option", { key: item }, item)))),
          h("label", { className: "check" }, h("input", { type: "checkbox", checked: handwriting, onChange: () => setHandwriting(!handwriting) }), "Difficult handwriting mode"),
          h("button", { className: "primary", onClick: run, disabled: !selected || busy }, busy ? "Extracting..." : "Extract Text"),
          h(Status, { message: error || status, error: Boolean(error) })
        ),
        h("div", { className: "image-preview" }, selectedFile ? h("img", { src: selectedFile.url, alt: "Preprocessed prescription" }) : "No preprocessed image available")
      ),
      h("div", { className: "output" }, result ? result.combined_text : "OCR output will appear here.")
    );
  }

  function Medicines({ ocrText, setOcrText, setMedicineRows, onRefresh }) {
    const [rows, setRows] = useState([]);
    const [status, setStatus] = useState("");
    const [error, setError] = useState("");
    const [busy, setBusy] = useState(false);

    async function run() {
      setBusy(true);
      setStatus("");
      setError("");

      try {
        const data = await api("/api/medicines", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ text: ocrText }),
        });
        setRows(data.medicines || []);
        setMedicineRows(data.medicines || []);
        setStatus(`Detected ${data.medicine_count} medicine item(s).`);
        await onRefresh();
      } catch (err) {
        setError(err.message);
      } finally {
        setBusy(false);
      }
    }

    return h(
      "section",
      { className: "panel" },
      h("div", { className: "panel-header" }, h("div", null, h("h3", null, "Medicine Detection"), h("p", null, "Review or edit OCR text, then detect medicines.")), h("button", { className: "primary", onClick: run, disabled: busy }, busy ? "Detecting..." : "Detect Medicines")),
      h("label", { className: "field" }, "OCR text", h("textarea", { value: ocrText, onChange: (event) => setOcrText(event.target.value), placeholder: "Run OCR first or paste prescription text here." })),
      h(Status, { message: error || status, error: Boolean(error) }),
      h(DataTable, { rows })
    );
  }

  function Benefits({ medicineRows, files, onRefresh }) {
    const [rows, setRows] = useState([]);
    const [useApiGenai, setUseApiGenai] = useState(false);
    const [status, setStatus] = useState("");
    const [error, setError] = useState("");
    const [busy, setBusy] = useState(false);
    const latestMedicineCsv = files.medicines.find((file) => file.name.endsWith(".csv"));

    useEffect(() => {
      let cancelled = false;

      api("/api/benefits/latest")
        .then((data) => {
          if (cancelled) return;
          setRows(data.benefits || []);
          if (data.benefits && data.benefits.length) {
            setStatus(`Loaded latest generated benefits from ${data.json_file_path || "saved output"}.`);
          }
        })
        .catch(() => {});

      return () => {
        cancelled = true;
      };
    }, []);

    async function run() {
      setBusy(true);
      setStatus("");
      setError("");

      try {
        const payload = {
          medicines: medicineRows,
          medicine_file_path: medicineRows.length ? "" : (latestMedicineCsv ? latestMedicineCsv.path : ""),
          use_api_genai: useApiGenai,
        };
        const data = await api("/api/benefits", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });
        setRows(data.benefits || []);
        setStatus(`Generated benefits for ${data.total_medicines} medicine item(s). ${data.generation_status.join(" | ")}${data.input_file ? ` Source: ${data.input_file}` : ""}`);
        await onRefresh();
      } catch (err) {
        setError(err.message);
      } finally {
        setBusy(false);
      }
    }

    return h(
      "section",
      { className: "panel" },
      h(
        "div",
        { className: "panel-header" },
        h(
          "div",
          null,
          h("h3", null, "Medicine Benefits Explanation"),
          h("p", null, latestMedicineCsv ? `Generate patient-friendly explanations from ${latestMedicineCsv.name}.` : "Generate patient-friendly explanations from detected medicines.")
        ),
        h("button", { className: "primary", onClick: run, disabled: busy }, busy ? "Generating..." : "Generate Benefits")
      ),
      h(
        "label",
        { className: "check" },
        h("input", { type: "checkbox", checked: useApiGenai, onChange: () => setUseApiGenai(!useApiGenai) }),
        "Use API GenAI explanations when OPENAI_API_KEY is configured"
      ),
      h(Status, { message: error || status, error: Boolean(error) }),
      rows.length
        ? h(
            "div",
            { className: "benefit-card-grid" },
            rows.map((item) =>
              h(
                "article",
                { className: "benefit-card", key: `${item.medicine_name}-${item.category}` },
                h("div", { className: "card-header" }, h("img", { className: "card-logo", src: "/assets/ui_icons/benefits.png", alt: "" }), h("div", null, h("h3", { className: "card-title" }, item.medicine_name), h("p", { className: "card-subtitle" }, item.category))),
                h("p", null, item.benefit_explanation),
                h("small", null, item.generation_method),
                h("div", { className: "status" }, item.patient_note)
              )
            )
          )
        : h(
            "div",
            { className: "output" },
            h("p", null, latestMedicineCsv ? `Ready to generate from latest medicine file: ${latestMedicineCsv.name}` : "Run Medicine Detection first, then generate benefits here.")
          )
    );
  }

  function Interactions({ medicineRows, files, onRefresh }) {
    const [result, setResult] = useState(null);
    const [status, setStatus] = useState("");
    const [error, setError] = useState("");
    const [busy, setBusy] = useState(false);
    const latestMedicineCsv = files.medicines.find((file) => file.name.endsWith(".csv"));

    useEffect(() => {
      let cancelled = false;

      api("/api/interactions/latest")
        .then((data) => {
          if (cancelled) return;
          setResult(data);
          setStatus(`Loaded latest interaction result from ${data.json_file_path || "saved output"}.`);
        })
        .catch(() => {});

      return () => {
        cancelled = true;
      };
    }, []);

    async function run() {
      setBusy(true);
      setStatus("");
      setError("");

      try {
        const payload = {
          medicines: medicineRows,
          medicine_file_path: medicineRows.length ? "" : (latestMedicineCsv ? latestMedicineCsv.path : ""),
        };
        const data = await api("/api/interactions", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });
        setResult(data);
        setStatus(`Checked ${data.total_pairs_checked} pair(s). High: ${data.high_risk_count}, Moderate: ${data.moderate_risk_count}, Low: ${data.low_risk_count}.`);
        await onRefresh();
      } catch (err) {
        setError(err.message);
      } finally {
        setBusy(false);
      }
    }

    return h(
      "section",
      { className: "panel" },
      h(
        "div",
        { className: "panel-header" },
        h("div", null, h("h3", null, "Drug Interaction Warning System"), h("p", null, latestMedicineCsv ? `Check interactions from ${latestMedicineCsv.name}.` : "Run Medicine Detection first, then check interactions.")),
        h("button", { className: "primary", onClick: run, disabled: busy }, busy ? "Checking..." : "Check Drug Interactions")
      ),
      h(Status, { message: error || status, error: Boolean(error) }),
      result
        ? h(
            React.Fragment,
            null,
            h(
              "div",
              { className: "module-placeholder" },
              h("div", { className: "mini-card" }, h("strong", null, result.total_pairs_checked), h("span", null, "Total pairs checked")),
              h("div", { className: "mini-card" }, h("strong", null, result.high_risk_count), h("span", null, "High risk")),
              h("div", { className: "mini-card" }, h("strong", null, result.moderate_risk_count), h("span", null, "Moderate risk")),
              h("div", { className: "mini-card" }, h("strong", null, result.low_risk_count), h("span", null, "Low risk"))
            ),
            h(DataTable, { rows: result.interaction_results || [] })
          )
        : h("div", { className: "output" }, latestMedicineCsv ? `Ready to check interactions from latest medicine file: ${latestMedicineCsv.name}` : "No medicine file available yet.")
    );
  }

  function Recommendations({ medicineRows, files, onRefresh }) {
    const [result, setResult] = useState(null);
    const [status, setStatus] = useState("");
    const [error, setError] = useState("");
    const [busy, setBusy] = useState(false);
    const latestMedicineCsv = files.medicines.find((file) => file.name.endsWith(".csv"));

    useEffect(() => {
      let cancelled = false;

      api("/api/recommendations/latest")
        .then((data) => {
          if (cancelled) return;
          setResult(data);
          setStatus(`Loaded latest recommendations from ${data.json_file_path || "saved output"}.`);
        })
        .catch(() => {});

      return () => {
        cancelled = true;
      };
    }, []);

    async function run() {
      setBusy(true);
      setStatus("");
      setError("");

      try {
        const payload = {
          medicines: medicineRows,
          medicine_file_path: medicineRows.length ? "" : (latestMedicineCsv ? latestMedicineCsv.path : ""),
        };
        const data = await api("/api/recommendations", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });
        setResult(data);
        setStatus(`Generated recommendations for ${data.total_medicines} medicine item(s).`);
        await onRefresh();
      } catch (err) {
        setError(err.message);
      } finally {
        setBusy(false);
      }
    }

    const rows = result ? result.recommendations || [] : [];

    return h(
      "section",
      { className: "panel" },
      h(
        "div",
        { className: "panel-header" },
        h("div", null, h("h3", null, "Medicine Recommendation Engine"), h("p", null, latestMedicineCsv ? `Generate alternatives from ${latestMedicineCsv.name}.` : "Run Medicine Detection first, then generate recommendations.")),
        h("button", { className: "primary", onClick: run, disabled: busy }, busy ? "Generating..." : "Generate Recommendations")
      ),
      h(Status, { message: error || status, error: Boolean(error) }),
      rows.length
        ? h(
            React.Fragment,
            null,
            h(
              "div",
              { className: "module-placeholder" },
              h("div", { className: "mini-card" }, h("strong", null, rows.length), h("span", null, "Medicines reviewed")),
              h("div", { className: "mini-card" }, h("strong", null, rows.filter((row) => !String(row.recommendations).includes("No alternative")).length), h("span", null, "With suggestions")),
              h("div", { className: "mini-card" }, h("strong", null, rows.filter((row) => String(row.recommendations).includes("Doctor consultation")).length), h("span", null, "Need doctor review"))
            ),
            h(DataTable, { rows })
          )
        : h("div", { className: "output" }, latestMedicineCsv ? `Ready to generate recommendations from latest medicine file: ${latestMedicineCsv.name}` : "No medicine file available yet.")
    );
  }

  function Dosage({ ocrText }) {
    const [result, setResult] = useState(null);
    const [status, setStatus] = useState("");
    const [error, setError] = useState("");
    const [busy, setBusy] = useState(false);

    async function run() {
      setBusy(true);
      setStatus("");
      setError("");

      try {
        const data = await api("/api/dosage", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ text: ocrText }),
        });
        setResult(data);
        setStatus("Dosage and timing extraction completed.");
      } catch (err) {
        setError(err.message);
      } finally {
        setBusy(false);
      }
    }

    return h(
      "section",
      { className: "panel" },
      h("div", { className: "panel-header" }, h("div", null, h("h3", null, "Dosage and Timing"), h("p", null, "Extract medicines, dosages, timings, and frequency terms.")), h("button", { className: "primary", onClick: run, disabled: busy }, busy ? "Extracting..." : "Extract Dosage")),
      h(Status, { message: error || status, error: Boolean(error) }),
      h("div", { className: "module-placeholder" },
        h("div", { className: "mini-card" }, h("strong", null, result ? result.medicines.length : 0), h("span", null, "Medicines")),
        h("div", { className: "mini-card" }, h("strong", null, result ? result.dosages.length : 0), h("span", null, "Dosages")),
        h("div", { className: "mini-card" }, h("strong", null, result ? result.timings.length : 0), h("span", null, "Timings"))
      ),
      h(DataTable, { rows: result ? result.medicines : [] })
    );
  }

  function Dashboard() {
    const [data, setData] = useState(null);
    const [status, setStatus] = useState("");
    const [error, setError] = useState("");
    const [busy, setBusy] = useState(false);

    async function loadDashboard() {
      setBusy(true);
      setError("");
      try {
        const result = await api("/api/dashboard");
        setData(result);
        setStatus(`Loaded dashboard: ${result.completed_steps}/${result.total_steps} steps completed.`);
      } catch (err) {
        setError(err.message);
      } finally {
        setBusy(false);
      }
    }

    useEffect(() => {
      loadDashboard();
    }, []);

    const counts = data ? data.counts : {};
    const files = data ? data.files : {};

    return h(
      "section",
      { className: "panel" },
      h(
        "div",
        { className: "panel-header" },
        h("div", null, h("h3", null, "Interactive Prescription Intelligence Dashboard"), h("p", null, "Latest outputs from the FastAPI pipeline.")),
        h("button", { className: "primary", onClick: loadDashboard, disabled: busy }, busy ? "Refreshing..." : "Refresh Dashboard")
      ),
      h(Status, { message: error || status, error: Boolean(error) }),
      h(
        "div",
        { className: "summary-card-grid" },
        h(SummaryCard, { icon: "/assets/ui_icons/dashboard.png", label: "Completed", value: data ? `${data.completed_steps}/${data.total_steps}` : "0/8", caption: "Workflow steps" }),
        h(SummaryCard, { icon: "/assets/ui_icons/medicines.png", label: "Medicines", value: counts.medicines || 0, caption: "Detected rows" }),
        h(SummaryCard, { icon: "/assets/ui_icons/dosage.png", label: "Dosage", value: counts.dosage || 0, caption: "Timing rows" }),
        h(SummaryCard, { icon: "/assets/ui_icons/interactions.png", label: "High Risk", value: counts.high_risk_interactions || 0, caption: "Interaction warnings" }),
        h(SummaryCard, { icon: "/assets/ui_icons/recommendations.png", label: "Recommendations", value: counts.recommendations || 0, caption: "Suggestion rows" })
      ),
      h(
        "div",
        { className: "grid-2 dashboard-images" },
        h(
          "div",
          null,
          h("h3", null, "Uploaded Prescription"),
          h("div", { className: "image-preview" }, files.uploaded_image ? h("img", { src: files.uploaded_image.url, alt: "Uploaded prescription" }) : "No uploaded image found.")
        ),
        h(
          "div",
          null,
          h("h3", null, "Preprocessed Image"),
          h("div", { className: "image-preview" }, files.preprocessed_image ? h("img", { src: files.preprocessed_image.url, alt: "Preprocessed prescription" }) : "No preprocessed image found.")
        )
      ),
      h("h3", null, "OCR Extracted Text"),
      h("div", { className: "output" }, data && data.ocr_text ? data.ocr_text : "No OCR text found."),
      h("h3", null, "Detected Medicines"),
      h(DataTable, { rows: data ? data.medicines : [] }),
      h("h3", null, "Dosage & Timing"),
      h(DataTable, { rows: data ? data.dosage : [] }),
      h("h3", null, "Medicine Benefits"),
      h(DataTable, { rows: data ? data.benefits : [] }),
      h("h3", null, "Drug Interaction Warnings"),
      h(DataTable, { rows: data ? data.interactions : [] }),
      h("h3", null, "Medicine Recommendations"),
      h(DataTable, { rows: data ? data.recommendations : [] }),
      h(
        "div",
        { className: "medical-disclaimer" },
        h("div", null, h("strong", null, "Medical Disclaimer"), h("p", null, "This dashboard is for educational support only. Always consult a qualified doctor or pharmacist before taking or changing medicines."))
      )
    );
  }

  function Database({ user }) {
    const [status, setStatus] = useState(null);
    const [records, setRecords] = useState([]);
    const [message, setMessage] = useState("");
    const [error, setError] = useState("");
    const [busy, setBusy] = useState(false);

    async function loadStatus() {
      setError("");
      try {
        const data = await api("/api/database/status");
        setStatus(data);
      } catch (err) {
        setError(err.message);
      }
    }

    async function loadRecords() {
      setError("");
      try {
        const query = user ? `?user_id=${encodeURIComponent(user)}` : "";
        const data = await api(`/api/database/records${query}`);
        setRecords(data.records || []);
        setMessage(data.error || `Loaded ${(data.records || []).length} stored prescription record(s).`);
      } catch (err) {
        setError(err.message);
      }
    }

    async function storeLatest() {
      setBusy(true);
      setMessage("");
      setError("");
      try {
        const data = await api("/api/database/store-latest", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ user_id: user || "Guest", file_name: "latest_prescription" }),
        });
        setMessage(`Stored latest analysis. Prescription ID: ${data.prescription_id}`);
        await loadStatus();
        await loadRecords();
      } catch (err) {
        setError(err.message);
      } finally {
        setBusy(false);
      }
    }

    useEffect(() => {
      loadStatus();
      loadRecords();
    }, [user]);

    const collections = status ? status.collections || {} : {};

    return h(
      "section",
      { className: "panel" },
      h(
        "div",
        { className: "panel-header" },
        h("div", null, h("h3", null, "Database Storage & Report Generation"), h("p", null, user ? `Database records for ${user}.` : "Login to store records under your name, or use Guest.")),
        h("div", { className: "button-row" }, h("button", { className: "secondary", onClick: loadStatus }, "Refresh"), h("button", { className: "primary", onClick: storeLatest, disabled: busy }, busy ? "Storing..." : "Store Latest Analysis"))
      ),
      h(Status, { message: error || message, error: Boolean(error) }),
      h(
        "div",
        { className: "module-placeholder" },
        h("div", { className: "mini-card" }, h("strong", null, status ? status.status : "Checking"), h("span", null, "MongoDB connection")),
        h("div", { className: "mini-card" }, h("strong", null, collections.prescriptions ? collections.prescriptions.total_documents : 0), h("span", null, "Prescriptions")),
        h("div", { className: "mini-card" }, h("strong", null, collections.medicines ? collections.medicines.total_documents : 0), h("span", null, "Medicines")),
        h("div", { className: "mini-card" }, h("strong", null, collections.reports ? collections.reports.total_documents : 0), h("span", null, "Reports"))
      ),
      status && status.status === "disconnected"
        ? h("div", { className: "status error" }, `MongoDB not connected: ${status.error || "Check MONGODB_URI or start MongoDB."}`)
        : null,
      h("h3", null, "Stored Prescriptions"),
      records.length
        ? h(
            "div",
            { className: "benefit-card-grid" },
            records.map((record) =>
              h(
                "article",
                { className: "benefit-card", key: record._id },
                h("div", { className: "card-header" }, h("img", { className: "card-logo", src: "/assets/ui_icons/database.png", alt: "" }), h("div", null, h("h3", { className: "card-title" }, record.file_name || "Prescription"), h("p", { className: "card-subtitle" }, record.created_at || ""))),
                h("p", null, `User: ${record.user_id || "N/A"}`),
                h("p", null, `Medicines: ${(record.medicines || []).length} | Dosage: ${(record.dosage || []).length} | Benefits: ${(record.benefits || []).length}`)
              )
            )
          )
        : h("div", { className: "output" }, status && status.status === "connected" ? "No stored prescription records found." : "Connect MongoDB to view stored records.")
    );
  }

  function DataTable({ rows }) {
    if (!rows || rows.length === 0) {
      return h("div", { className: "output" }, "No rows yet.");
    }

    const columns = Object.keys(rows[0]);
    return h(
      "div",
      { className: "table-wrap" },
      h(
        "table",
        null,
        h("thead", null, h("tr", null, columns.map((column) => h("th", { key: column }, column.replaceAll("_", " "))))),
        h(
          "tbody",
          null,
          rows.map((row, index) =>
            h("tr", { key: index }, columns.map((column) => h("td", { key: column }, String(row[column] ?? ""))))
          )
        )
      )
    );
  }

  function LoginModal({ open, user, onClose, onSave }) {
    const [name, setName] = useState(user || "");
    const inputRef = useRef(null);

    useEffect(() => {
      if (!open) return;
      setName(user || "");
      const focusTimer = window.setTimeout(() => inputRef.current && inputRef.current.focus(), 80);

      function handleKeydown(event) {
        if (event.key === "Escape") onClose();
      }

      window.addEventListener("keydown", handleKeydown);
      return () => {
        window.clearTimeout(focusTimer);
        window.removeEventListener("keydown", handleKeydown);
      };
    }, [open, user, onClose]);

    if (!open) return null;

    function submit(event) {
      event.preventDefault();
      const cleanName = name.trim();
      if (!cleanName) return;
      onSave(cleanName);
    }

    return h(
      "div",
      { className: "login-modal-backdrop", role: "presentation", onMouseDown: onClose },
      h(
        "section",
        {
          className: "login-modal",
          role: "dialog",
          "aria-modal": "true",
          "aria-labelledby": "login-title",
          onMouseDown: (event) => event.stopPropagation(),
        },
        h(
          "div",
          { className: "login-modal-visual" },
          h("img", { src: "/assets/ai_prescription_logo.png", alt: "" }),
          h("span", null, "Secure workspace")
        ),
        h(
          "form",
          { className: "login-modal-form", onSubmit: submit },
          h(
            "div",
            { className: "login-modal-header" },
            h("div", null, h("p", { className: "login-kicker" }, "Welcome"), h("h2", { id: "login-title" }, user ? "Change user" : "Login")),
            h("button", { type: "button", className: "login-close", onClick: onClose, "aria-label": "Close login popup" }, "x")
          ),
          h("p", { className: "login-modal-copy" }, "Enter your name to save prescriptions, reports, and database records under your workspace."),
          h(
            "label",
            { className: "login-field" },
            "Your name",
            h("input", {
              ref: inputRef,
              value: name,
              onChange: (event) => setName(event.target.value),
              placeholder: "Example: Priya Sharma",
              autoComplete: "name",
            })
          ),
          h(
            "div",
            { className: "login-modal-actions" },
            h("button", { type: "button", className: "secondary", onClick: onClose }, "Cancel"),
            h("button", { type: "submit", className: "primary", disabled: !name.trim() }, user ? "Update User" : "Continue")
          )
        )
      )
    );
  }

  function App() {
    const [active, setActive] = useState("home");
    const [files, setFiles] = useState({ uploads: [], preprocessed: [], ocr: [], medicines: [], dosage: [], benefits: [], interactions: [] });
    const [ocrText, setOcrText] = useState("");
    const [medicineRows, setMedicineRows] = useState([]);
    const [user, setUser] = useState(() => localStorage.getItem("prescriptionReaderUser") || "");
    const [loginOpen, setLoginOpen] = useState(false);

    async function refreshFiles() {
      const data = await api("/api/files");
      setFiles({
        uploads: data.uploads || [],
        preprocessed: data.preprocessed || [],
        ocr: data.ocr || [],
        medicines: data.medicines || [],
        dosage: data.dosage || [],
        benefits: data.benefits || [],
        interactions: data.interactions || [],
      });
    }

    function handleLogin() {
      setLoginOpen(true);
    }

    function handleLoginSave(cleanName) {
      localStorage.setItem("prescriptionReaderUser", cleanName);
      setUser(cleanName);
      setLoginOpen(false);
    }

    function handleLogout() {
      localStorage.removeItem("prescriptionReaderUser");
      setUser("");
    }

    async function handleClearOutputs() {
      const ok = window.confirm("Clear all generated outputs? Uploaded files, OCR text, medicines, benefits, interactions, and reports will be deleted from output folders.");
      if (!ok) return;

      const data = await api("/api/clear-outputs", { method: "POST" });
      setOcrText("");
      setMedicineRows([]);
      await refreshFiles();
      window.alert(`Cleared ${data.deleted_files} file(s).`);
    }

    useEffect(() => {
      refreshFiles().catch(() => {});
    }, []);

    const screen = useMemo(() => {
      if (active === "upload") return h(Upload, { onRefresh: refreshFiles });
      if (active === "preprocess") return h(Preprocess, { files, onRefresh: refreshFiles });
      if (active === "ocr") return h(OCR, { files, onRefresh: refreshFiles, setOcrText });
      if (active === "medicines") return h(Medicines, { ocrText, setOcrText, setMedicineRows, onRefresh: refreshFiles });
      if (active === "dosage") return h(Dosage, { ocrText });
      if (active === "benefits") return h(Benefits, { medicineRows, files, onRefresh: refreshFiles });
      if (active === "interactions") return h(Interactions, { medicineRows, files, onRefresh: refreshFiles });
      if (active === "recommendations") return h(Recommendations, { medicineRows, files, onRefresh: refreshFiles });
      if (active === "dashboard") return h(Dashboard);
      if (active === "database") return h(Database, { user });
      if ([].includes(active)) {
        const current = modules.find((item) => item.id === active);
        return h(
          "section",
          { className: "professional-card" },
          h("div", { className: "card-header" }, h("img", { className: "card-logo", src: current.icon, alt: "" }), h("div", null, h("h3", { className: "card-title" }, current.label), h("p", { className: "card-subtitle" }, "This module keeps the original workspace style and can be connected to the next API step.")))
        );
      }
      return h(Home, { files, user, onLogin: handleLogin, onClearOutputs: handleClearOutputs });
    }, [active, files, ocrText, medicineRows, user]);

    return h(
      "div",
      { className: "shell" },
      h(Topbar, { user, onLogin: handleLogin, onLogout: handleLogout }),
      h(LoginModal, { open: loginOpen, user, onClose: () => setLoginOpen(false), onSave: handleLoginSave }),
      h(ModuleNav, { active, setActive }),
      h(
        "main",
        { className: "main" },
        h(WorkspaceOverview, { active, files, setActive }),
        screen,
        h(StepControls, { active, setActive })
      )
    );
  }

  ReactDOM.createRoot(document.getElementById("root")).render(h(App));
})();
