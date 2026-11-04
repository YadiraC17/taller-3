import { api } from "./api.js";

const $ = (selector, root = document) => root.querySelector(selector);
const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];
const monthNames = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"];
const state = { user: null, categories: [], transactions: [], budgets: [], summary: null, expenses: [], evolution: [] };
let currentEntity = null;
let currentId = null;
let toastTimer;

function escapeHtml(value = "") {
  return String(value).replace(/[&<>"']/g, (character) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[character]);
}

function period() {
  const [year, month] = $("#period-input").value.split("-").map(Number);
  return { mes: month, anio: year };
}

function periodQuery() {
  const { mes, anio } = period();
  return `mes=${mes}&anio=${anio}`;
}

function localDateString() {
  const today = new Date();
  return `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, "0")}-${String(today.getDate()).padStart(2, "0")}`;
}

function money(value, currency) {
  return new Intl.NumberFormat("es-PE", { style: "currency", currency, minimumFractionDigits: 2 }).format(Number(value || 0));
}

function toast(message, error = false) {
  const element = $("#toast");
  element.textContent = message;
  element.classList.toggle("error", error);
  element.classList.add("visible");
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => element.classList.remove("visible"), 3200);
}

function showAuth(message = "") {
  state.user = null;
  $("#app-view").classList.add("hidden");
  $("#auth-view").classList.remove("hidden");
  $("#auth-message").textContent = message;
}

function showApp(user) {
  state.user = user;
  $("#auth-view").classList.add("hidden");
  $("#app-view").classList.remove("hidden");
  $("#user-name").textContent = user.nombre;
  $("#user-initial").textContent = user.nombre.trim().charAt(0).toUpperCase();
  $("#topbar-user").textContent = `Hola, ${user.nombre.split(" ")[0]}`;
  loadData();
}

function setView(name) {
  $$(".page-view").forEach((view) => view.classList.toggle("active", view.id === `${name}-view`));
  $$(".nav-link").forEach((link) => link.classList.toggle("active", link.dataset.view === name));
  if (name === "transacciones") loadTransactions();
}

async function loadData() {
  const query = periodQuery();
  try {
    const [categories, transactions, budgets, summary, expenses, evolution] = await Promise.all([
      api.request("/categorias"),
      api.request("/transacciones"),
      api.request(`/presupuestos/seguimiento?${query}`),
      api.request(`/reportes/resumen?${query}`),
      api.request(`/reportes/gastos-categoria?${query}`),
      api.request(`/reportes/evolucion?anio=${period().anio}`),
    ]);
    Object.assign(state, { categories, transactions, budgets, summary, expenses, evolution: evolution.meses });
    renderAll();
  } catch (error) {
    toast(error.message, true);
  }
}

function renderAll() {
  renderCurrencies($("#dashboard-currencies"));
  renderCurrencies($("#report-summary"));
  renderCategoryBars($("#dashboard-expenses"), state.expenses);
  renderCategoryBars($("#report-expenses"), state.expenses);
  renderBudgets($("#dashboard-budgets"), state.budgets.slice(0, 3), true);
  renderBudgets($("#budgets-list"), state.budgets, false);
  renderTransactionsTable($("#dashboard-recent"), state.transactions.slice(0, 6), false);
  renderTransactionsTable($("#transactions-table"), state.transactions, true);
  renderCategories();
  renderEvolution();
}

function renderCurrencies(container) {
  if (!state.summary) return;
  container.innerHTML = ["PEN", "USD"].map((currency) => {
    const values = state.summary[currency];
    return `<article class="currency-card ${currency.toLowerCase()}">
      <div class="currency-card-head"><span class="currency-tag">${currency}</span><span>${currency === "PEN" ? "Sol peruano" : "Dólar estadounidense"}</span></div>
      <div class="currency-values">
        <div class="currency-value"><span>Ingresos</span><strong>${money(values.ingresos, currency)}</strong></div>
        <div class="currency-value"><span>Gastos</span><strong>${money(values.gastos, currency)}</strong></div>
        <div class="currency-value balance"><span>Balance</span><strong>${money(values.balance, currency)}</strong></div>
      </div>
    </article>`;
  }).join("");
}

function renderCategoryBars(container, entries) {
  if (!entries.length) {
    container.innerHTML = '<div class="empty-state">Aún no hay gastos registrados en este periodo.</div>';
    return;
  }
  const groups = ["PEN", "USD"].map((currency) => ({ currency, items: entries.filter((entry) => entry.moneda === currency) })).filter((group) => group.items.length);
  container.innerHTML = groups.map(({ currency, items }) => {
    const maximum = Math.max(...items.map((item) => Number(item.total)), 0.01);
    return `<div class="bar-group"><p class="currency-tag">${currency}</p>${items.map((item) => `<div class="bar-row">
      <span class="bar-name" title="${escapeHtml(item.categoria)}">${escapeHtml(item.categoria)}</span>
      <span class="bar-track"><span class="bar-fill" style="width:${Math.max(3, Number(item.total) / maximum * 100)}%"></span></span>
      <span class="bar-value">${money(item.total, currency)}</span>
    </div>`).join("")}</div>`;
  }).join("");
}

function transactionRows(items, actions) {
  if (!items.length) return '<div class="empty-state">No hay movimientos para mostrar.</div>';
  return `<table><thead><tr><th>Fecha</th><th>Detalle</th><th>Tipo</th><th>Monto</th>${actions ? "<th></th>" : ""}</tr></thead><tbody>${items.map((item) => `
    <tr><td>${escapeHtml(item.fecha)}</td><td>${escapeHtml(item.descripcion || item.categoria)}</td>
    <td><span class="type-pill ${item.tipo === "GASTO" ? "expense" : ""}">${item.tipo}</span></td>
    <td class="amount ${item.tipo === "GASTO" ? "expense" : "income"}">${item.tipo === "GASTO" ? "−" : "+"}${money(item.monto, item.moneda)}</td>
    ${actions ? `<td><div class="table-actions"><button class="table-action" data-action="edit-transaction" data-id="${item.id_transaccion}">Editar</button><button class="table-action danger" data-action="delete-transaction" data-id="${item.id_transaccion}">Eliminar</button></div></td>` : ""}</tr>`).join("")}</tbody></table>`;
}

function renderTransactionsTable(container, items, actions) {
  container.innerHTML = transactionRows(items, actions);
}

function budgetMarkup(item, actions) {
  const percent = Number(item.porcentaje_consumido);
  const statusClass = item.estado === "EXCEDIDO" ? "over" : item.estado === "CERCA_DEL_LIMITE" ? "near" : "";
  const statusLabel = item.estado === "EXCEDIDO" ? "Excedido" : item.estado === "CERCA_DEL_LIMITE" ? "Cerca del límite" : "Dentro del presupuesto";
  return `<article class="budget-item">
    <div class="budget-item-head"><strong>${escapeHtml(item.categoria)}</strong><span>${item.moneda} · ${item.mes}/${item.anio}</span></div>
    <div class="budget-track"><span class="${statusClass}" style="width:${Math.min(100, Math.max(0, percent))}%"></span></div>
    <div class="budget-meta"><span>${money(item.gasto_acumulado, item.moneda)} de ${money(item.monto_limite, item.moneda)}</span><span class="budget-status ${statusClass}">${Math.round(percent * 100) / 100}% · ${statusLabel}</span></div>
    <div class="budget-meta"><span>Disponible ${money(item.saldo_disponible, item.moneda)}</span>${actions ? `<span class="table-actions"><button class="table-action" data-action="edit-budget" data-id="${item.id_presupuesto}">Editar</button><button class="table-action danger" data-action="delete-budget" data-id="${item.id_presupuesto}">Eliminar</button></span>` : ""}</div>
  </article>`;
}

function renderBudgets(container, items, compact) {
  container.classList.toggle("compact", compact);
  container.innerHTML = items.length ? items.map((item) => budgetMarkup(item, !compact)).join("") : '<div class="empty-state">No hay presupuestos para este periodo.</div>';
}

function renderCategories() {
  const container = $("#categories-table");
  if (!state.categories.length) {
    container.innerHTML = '<div class="empty-state">Todavía no tienes categorías. Crea una para empezar.</div>';
    return;
  }
  container.innerHTML = `<table><thead><tr><th>Nombre</th><th>Tipo</th><th>Descripción</th><th></th></tr></thead><tbody>${state.categories.map((item) => `
    <tr><td><strong>${escapeHtml(item.nombre)}</strong></td><td><span class="type-pill ${item.tipo === "GASTO" ? "expense" : ""}">${item.tipo}</span></td>
    <td>${escapeHtml(item.descripcion || "—")}</td><td><div class="table-actions"><button class="table-action" data-action="edit-category" data-id="${item.id_categoria}">Editar</button><button class="table-action danger" data-action="delete-category" data-id="${item.id_categoria}">Eliminar</button></div></td></tr>`).join("")}</tbody></table>`;
}

function renderEvolution() {
  const container = $("#report-evolution");
  container.innerHTML = `<div class="evolution-currencies">${["PEN", "USD"].map((currency) => {
    const maximum = Math.max(1, ...state.evolution.flatMap((month) => [month[currency].ingresos, month[currency].gastos]));
    return `<section class="evolution-currency"><div class="currency-card-head"><span class="currency-tag">${currency}</span><span>Ingresos y gastos</span></div><div class="evolution-chart">${state.evolution.map((month) => `
      <div class="month-column"><div class="month-bars" title="${monthNames[month.mes - 1]}: ingresos ${money(month[currency].ingresos, currency)}, gastos ${money(month[currency].gastos, currency)}">
        <span style="height:${month[currency].ingresos ? Math.max(2, month[currency].ingresos / maximum * 100) : 0}%"></span><span style="height:${month[currency].gastos ? Math.max(2, month[currency].gastos / maximum * 100) : 0}%"></span></div><span class="month-name">${monthNames[month.mes - 1]}</span></div>`).join("")}</div></section>`;
  }).join("")}</div><div class="evolution-legend"><span class="legend-income">Ingresos</span><span class="legend-expense">Gastos</span></div>`;
}

async function loadTransactions(query = "") {
  try {
    state.transactions = await api.request(`/transacciones${query ? `?${query}` : ""}`);
    renderTransactionsTable($("#transactions-table"), state.transactions, true);
    renderTransactionsTable($("#dashboard-recent"), state.transactions.slice(0, 6), false);
  } catch (error) {
    toast(error.message, true);
  }
}

function field(label, name, type = "text", value = "", extra = "") {
  const escaped = escapeHtml(value);
  return `<label>${label}<input name="${name}" type="${type}" value="${escaped}" ${extra} required></label>`;
}

function categoryOptions(type, selected = "") {
  return state.categories.filter((category) => !type || category.tipo === type).map((category) =>
    `<option value="${category.id_categoria}" ${String(category.id_categoria) === String(selected) ? "selected" : ""}>${escapeHtml(category.nombre)}</option>`).join("");
}

function openDialog(kind, item = null) {
  currentEntity = kind;
  currentId = item ? item[{ category: "id_categoria", transaction: "id_transaccion", budget: "id_presupuesto" }[kind]] : null;
  const title = { category: item ? "Editar categoría" : "Nueva categoría", transaction: item ? "Editar movimiento" : "Registrar movimiento", budget: item ? "Editar presupuesto" : "Nuevo presupuesto" }[kind];
  $("#dialog-title").textContent = title;
  $("#dialog-eyebrow").textContent = { category: "ORGANIZACIÓN", transaction: "MOVIMIENTO FINANCIERO", budget: "LÍMITE MENSUAL" }[kind];
  let markup = "";
  if (kind === "category") {
    markup = `${field("Nombre", "nombre", "text", item?.nombre || "", "maxlength='80'")}<label>Tipo<select name="tipo" required><option value="GASTO" ${item?.tipo !== "INGRESO" ? "selected" : ""}>GASTO</option><option value="INGRESO" ${item?.tipo === "INGRESO" ? "selected" : ""}>INGRESO</option></select></label><label>Descripción<input name="descripcion" maxlength="255" value="${escapeHtml(item?.descripcion || "")}"></label>`;
  } else if (kind === "transaction") {
    const type = item?.tipo || "GASTO";
    markup = `<label>Tipo<select name="tipo" required><option ${type === "GASTO" ? "selected" : ""}>GASTO</option><option ${type === "INGRESO" ? "selected" : ""}>INGRESO</option></select></label><label>Categoría<select name="id_categoria" required>${categoryOptions(type, item?.id_categoria)}</select></label>${field("Monto", "monto", "number", item?.monto || "", "min='0.01' step='0.01'")}<label>Moneda<select name="moneda" required><option ${item?.moneda !== "USD" ? "selected" : ""}>PEN</option><option ${item?.moneda === "USD" ? "selected" : ""}>USD</option></select></label>${field("Fecha", "fecha", "date", item?.fecha || localDateString())}<label>Descripción<input name="descripcion" maxlength="255" value="${escapeHtml(item?.descripcion || "")}"></label>`;
  } else {
    const now = new Date();
    const expenseCategories = state.categories.filter((category) => category.tipo === "GASTO");
    markup = `<label>Categoría de gasto<select name="id_categoria" required>${categoryOptions("GASTO", item?.id_categoria)}</select></label>${field("Monto límite", "monto_limite", "number", item?.monto_limite || "", "min='0.01' step='0.01'")}<label>Moneda<select name="moneda" required><option ${item?.moneda !== "USD" ? "selected" : ""}>PEN</option><option ${item?.moneda === "USD" ? "selected" : ""}>USD</option></select></label><div class="form-row">${field("Mes", "mes", "number", item?.mes || now.getMonth() + 1, "min='1' max='12'")}${field("Año", "anio", "number", item?.anio || now.getFullYear(), "min='2000' max='9998'")}</div>`;
    if (!expenseCategories.length) toast("Primero crea una categoría de tipo GASTO.", true);
  }
  $("#dialog-fields").innerHTML = markup;
  const typeSelect = $("#dialog-fields select[name='tipo']");
  if (kind === "transaction" && typeSelect) {
    typeSelect.addEventListener("change", () => {
      $("#dialog-fields select[name='id_categoria']").innerHTML = categoryOptions(typeSelect.value);
    });
  }
  $("#entity-dialog").showModal();
}

function entityFromButton(button) {
  const id = Number(button.dataset.id);
  if (button.dataset.action.includes("category")) return state.categories.find((item) => item.id_categoria === id);
  if (button.dataset.action.includes("transaction")) return state.transactions.find((item) => item.id_transaccion === id);
  return state.budgets.find((item) => item.id_presupuesto === id);
}

async function deleteEntity(kind, item) {
  const config = {
    category: { path: `/categorias/${item.id_categoria}`, label: "categoría" },
    transaction: { path: `/transacciones/${item.id_transaccion}`, label: "movimiento" },
    budget: { path: `/presupuestos/${item.id_presupuesto}`, label: "presupuesto" },
  }[kind];
  if (!window.confirm(`¿Eliminar este ${config.label}?`)) return;
  try {
    await api.request(config.path, { method: "DELETE" });
    toast("Registro eliminado.");
    await loadData();
  } catch (error) {
    toast(error.message, true);
  }
}

$("#period-input").value = localDateString().slice(0, 7);

$$('[data-auth-mode]').forEach((button) => button.addEventListener("click", () => {
  const register = button.dataset.authMode === "register";
  $$(".auth-tab").forEach((tab) => tab.classList.toggle("active", tab === button));
  $("#login-form").classList.toggle("hidden", register);
  $("#register-form").classList.toggle("hidden", !register);
  $("#auth-message").textContent = "";
}));

$("#login-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const values = Object.fromEntries(new FormData(event.currentTarget));
  try {
    showApp(await api.login(values));
    toast("Sesión iniciada.");
  } catch (error) {
    $("#auth-message").textContent = error.message;
  }
});

$("#register-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const values = Object.fromEntries(new FormData(event.currentTarget));
  if (values.password !== values.confirmacion) {
    $("#auth-message").textContent = "Las contraseñas no coinciden.";
    return;
  }
  delete values.confirmacion;
  try {
    await api.register(values);
    showApp(await api.login(values));
    toast("Cuenta creada correctamente.");
  } catch (error) {
    $("#auth-message").textContent = error.message;
  }
});

$("#logout-button").addEventListener("click", () => {
  api.clearSession();
  showAuth();
});

window.addEventListener("fintrack:session-expired", () => showAuth("La sesión expiró. Inicia sesión nuevamente."));

$$(".nav-link").forEach((button) => button.addEventListener("click", () => setView(button.dataset.view)));
$$("[data-view-link]").forEach((button) => button.addEventListener("click", () => setView(button.dataset.viewLink)));
$("#period-input").addEventListener("change", loadData);

$("#transaction-filters").addEventListener("submit", (event) => {
  event.preventDefault();
  const params = new URLSearchParams(Object.fromEntries(new FormData(event.currentTarget)));
  loadTransactions(params.toString());
});
$("#transaction-filters").addEventListener("reset", () => setTimeout(() => loadTransactions(), 0));

document.addEventListener("click", async (event) => {
  const closeButton = event.target.closest("[data-close-dialog]");
  if (closeButton) { $("#entity-dialog").close(); return; }
  const button = event.target.closest("[data-action]");
  if (!button) return;
  const action = button.dataset.action;
  if (action === "new-category") openDialog("category");
  if (action === "new-transaction") openDialog("transaction");
  if (action === "new-budget") openDialog("budget");
  if (action.startsWith("edit-")) openDialog(action.slice(5), entityFromButton(button));
  if (action.startsWith("delete-")) await deleteEntity(action.slice(7), entityFromButton(button));
});

$("#entity-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const payload = Object.fromEntries(new FormData(event.currentTarget));
  if (currentEntity === "transaction") {
    payload.id_categoria = Number(payload.id_categoria);
    payload.monto = Number(payload.monto);
  } else if (currentEntity === "budget") {
    payload.id_categoria = Number(payload.id_categoria);
    payload.monto_limite = Number(payload.monto_limite);
    payload.mes = Number(payload.mes);
    payload.anio = Number(payload.anio);
  }
  const paths = { category: "/categorias", transaction: "/transacciones", budget: "/presupuestos" };
  const path = `${paths[currentEntity]}${currentId ? `/${currentId}` : ""}`;
  try {
    await api.request(path, { method: currentId ? "PUT" : "POST", body: JSON.stringify(payload) });
    $("#entity-dialog").close();
    toast(currentId ? "Cambios guardados." : "Registro creado.");
    await loadData();
  } catch (error) {
    toast(error.message, true);
  }
});

async function boot() {
  if (!api.token) return;
  try {
    const data = await api.request("/auth/me");
    showApp(data.usuario);
  } catch {
    api.clearSession();
    showAuth();
  }
}

boot();