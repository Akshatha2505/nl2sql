const form = document.getElementById("question-form");
const questionInput = document.getElementById("question-input");
const submitBtn = document.getElementById("submit-btn");
const resultSection = document.getElementById("result");
const sqlOutput = document.getElementById("sql-output");
const rowsOutput = document.getElementById("rows-output");
const errorSection = document.getElementById("error");

form.addEventListener("submit", async (event) => {
  event.preventDefault();

  const question = questionInput.value.trim();
  if (!question) {
    return;
  }

  setLoading(true);
  hide(resultSection);
  hide(errorSection);

  try {
    const response = await fetch("/query", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question }),
    });

    const data = await response.json();

    if (!response.ok) {
      showError(data.detail || "Something went wrong.");
      return;
    }

    showResult(data);
  } catch (err) {
    showError("Could not reach the server. Please try again.");
  } finally {
    setLoading(false);
  }
});

function setLoading(isLoading) {
  submitBtn.disabled = isLoading;
  submitBtn.textContent = isLoading ? "Running..." : "Submit";
}

function showResult(data) {
  sqlOutput.textContent = data.sql;
  rowsOutput.innerHTML = "";
  rowsOutput.appendChild(buildTable(data.columns, data.rows));
  show(resultSection);
}

function buildTable(columns, rows) {
  const table = document.createElement("table");

  const thead = document.createElement("thead");
  const headRow = document.createElement("tr");
  columns.forEach((col) => {
    const th = document.createElement("th");
    th.textContent = col;
    headRow.appendChild(th);
  });
  thead.appendChild(headRow);
  table.appendChild(thead);

  const tbody = document.createElement("tbody");
  rows.forEach((row) => {
    const tr = document.createElement("tr");
    columns.forEach((col) => {
      const td = document.createElement("td");
      td.textContent = row[col] ?? "";
      tr.appendChild(td);
    });
    tbody.appendChild(tr);
  });
  table.appendChild(tbody);

  return table;
}

function showError(message) {
  errorSection.textContent = message;
  show(errorSection);
}

function show(el) {
  el.classList.remove("hidden");
}

function hide(el) {
  el.classList.add("hidden");
}
