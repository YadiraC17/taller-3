package pe.fintrack.android;

import android.app.Activity;
import android.app.AlertDialog;
import android.os.Bundle;
import android.text.InputType;
import android.view.Gravity;
import android.view.View;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.EditText;
import android.widget.HorizontalScrollView;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.Spinner;
import android.widget.TextView;
import android.widget.Toast;

import org.json.JSONArray;
import org.json.JSONObject;

import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Date;
import java.util.Locale;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public class MainActivity extends Activity {
    private static final String DEFAULT_API_BASE = "https://fintrack-api-392k.onrender.com/api";
    private static final int FOREST = 0xFF143D35;
    private static final int TEAL = 0xFF367F70;
    private static final int INK = 0xFF1B2C28;
    private static final int MUTED = 0xFF68766F;
    private static final int CANVAS = 0xFFF3F5F0;
    private static final int WHITE = 0xFFFFFFFF;

    private final ExecutorService executor = Executors.newSingleThreadExecutor();
    private android.content.SharedPreferences preferences;
    private String apiBase;
    private String token;
    private String userName = "";
    private LinearLayout pageContent;
    private EditText periodField;

    private interface ApiSuccess {
        void onSuccess(JSONObject response);
    }

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        getWindow().setStatusBarColor(FOREST);
        getWindow().setNavigationBarColor(FOREST);
        preferences = getSharedPreferences("fintrack_android", MODE_PRIVATE);
        String savedApiBase = preferences.getString("api_base", "");
        apiBase = isDebugBuild() && !savedApiBase.trim().isEmpty()
                ? savedApiBase
                : DEFAULT_API_BASE;
        token = preferences.getString("access_token", "");
        if (token.isEmpty()) {
            showLogin();
        } else {
            callApi("/auth/me", "GET", null, response -> {
                JSONObject user = response.optJSONObject("data").optJSONObject("usuario");
                userName = user == null ? "" : user.optString("nombre", "");
                showDashboard();
            });
        }
    }

    @Override
    protected void onDestroy() {
        executor.shutdownNow();
        super.onDestroy();
    }

    private void callApi(String path, String method, JSONObject body, ApiSuccess success) {
        executor.execute(() -> {
            try {
                JSONObject response = ApiClient.request(apiBase, path, method, token, body);
                runOnUiThread(() -> success.onSuccess(response));
            } catch (Exception error) {
                runOnUiThread(() -> {
                    if (error instanceof ApiClient.HttpError
                            && ((ApiClient.HttpError) error).statusCode == 401
                            && !token.isEmpty()) {
                        clearSession();
                        showLogin();
                        Toast.makeText(this, "La sesión expiró. Inicia sesión nuevamente.", Toast.LENGTH_LONG).show();
                    } else if (pageContent == null && !token.isEmpty()) {
                        clearSession();
                        showLogin();
                        Toast.makeText(this, "No se pudo validar la sesión. Revisa la URL del servidor y la conexión.", Toast.LENGTH_LONG).show();
                    } else {
                        Toast.makeText(this, error.getMessage() == null ? "Error de conexión con la API" : error.getMessage(), Toast.LENGTH_LONG).show();
                    }
                });
            }
        });
    }

    private void showLogin() {
        token = "";
        LinearLayout root = baseColumn();
        root.setGravity(Gravity.CENTER_VERTICAL);
        root.setPadding(dp(24), dp(28), dp(24), dp(28));
        TextView brand = text("FINTRACK", 30, FOREST, true);
        root.addView(brand);
        TextView subtitle = text("Tus finanzas, desde tu móvil", 15, MUTED, false);
        subtitle.setPadding(0, 0, 0, dp(22));
        root.addView(subtitle);

        EditText nameInput = input("Nombre", InputType.TYPE_CLASS_TEXT | InputType.TYPE_TEXT_FLAG_CAP_WORDS);
        root.addView(nameInput);
        EditText emailInput = input("Correo electrónico", InputType.TYPE_CLASS_TEXT | InputType.TYPE_TEXT_VARIATION_EMAIL_ADDRESS);
        root.addView(emailInput);
        EditText passwordInput = input("Contraseña (mínimo 8 caracteres)", InputType.TYPE_CLASS_TEXT | InputType.TYPE_TEXT_VARIATION_PASSWORD);
        root.addView(passwordInput);
        TextView message = text("", 13, MUTED, false);
        message.setPadding(0, dp(8), 0, dp(8));
        root.addView(message);

        Button loginButton = button("Iniciar sesión", FOREST);
        if (isDebugBuild()) {
            Button serverButton = smallButton("Servidor");
            root.addView(serverButton);
            serverButton.setOnClickListener(view -> showApiConfigDialog());
        }
        root.addView(loginButton);
        Button registerButton = button("Crear cuenta", TEAL);
        root.addView(registerButton);
        setContentView(root);

        loginButton.setOnClickListener(view -> {
            JSONObject payload = new JSONObject();
            try {
                payload.put("correo", emailInput.getText().toString().trim());
                payload.put("password", passwordInput.getText().toString());
            } catch (Exception ignored) {
                message.setText("No se pudo preparar la solicitud.");
                return;
            }
            callLogin(payload, message);
        });

        registerButton.setOnClickListener(view -> {
            if (nameInput.getText().toString().trim().isEmpty()) {
                message.setText("Escribe tu nombre para crear la cuenta.");
                return;
            }
            JSONObject payload = new JSONObject();
            try {
                payload.put("nombre", nameInput.getText().toString().trim());
                payload.put("correo", emailInput.getText().toString().trim());
                payload.put("password", passwordInput.getText().toString());
            } catch (Exception ignored) {
                message.setText("No se pudo preparar la solicitud.");
                return;
            }
            callApi("/auth/register", "POST", payload, response -> {
                JSONObject credentials = new JSONObject();
                try {
                    credentials.put("correo", emailInput.getText().toString().trim());
                    credentials.put("password", passwordInput.getText().toString());
                    message.setText("Cuenta creada. Iniciando sesión...");
                    callLogin(credentials, message);
                } catch (Exception error) {
                    message.setText(error.getMessage());
                }
            });
        });
    }

    private void callLogin(JSONObject payload, TextView message) {
        callApi("/auth/login", "POST", payload, response -> {
            JSONObject data = response.optJSONObject("data");
            if (data == null) {
                message.setText("Respuesta de autenticación no válida.");
                return;
            }
            token = data.optString("access_token", "");
            JSONObject user = data.optJSONObject("usuario");
            userName = user == null ? "" : user.optString("nombre", "");
            preferences.edit().putString("access_token", token).apply();
            showDashboard();
        });
    }

    private void showDashboard() {
        installScreen("Resumen");
        pageContent.addView(text("Hola, " + (userName.isEmpty() ? "bienvenido" : userName), 20, INK, true));
        periodField = input("Periodo YYYY-MM", InputType.TYPE_CLASS_TEXT);
        periodField.setText(new SimpleDateFormat("yyyy-MM", Locale.US).format(new Date()));
        pageContent.addView(periodField);
        Button refresh = button("Actualizar resumen", TEAL);
        pageContent.addView(refresh);
        refresh.setOnClickListener(view -> loadSummary());
        loadSummary();
    }

    private void loadSummary() {
        String[] period = getPeriod();
        callApi("/reportes/resumen?mes=" + period[0] + "&anio=" + period[1], "GET", null, response -> {
            pageContent.removeViews(3, Math.max(0, pageContent.getChildCount() - 3));
            JSONObject data = response.optJSONObject("data");
            if (data == null) return;
            pageContent.addView(currencyPanel("PEN", data.optJSONObject("PEN")));
            pageContent.addView(currencyPanel("USD", data.optJSONObject("USD")));
            addText("Periodo " + period[0] + "/" + period[1], 13, MUTED, false);
        });
    }

    private View currencyPanel(String currency, JSONObject values) {
        LinearLayout panel = card();
        panel.addView(text(currency, 14, TEAL, true));
        if (values != null) {
            panel.addView(text("Ingresos: " + amount(values.optDouble("ingresos"), currency), 14, INK, false));
            panel.addView(text("Gastos: " + amount(values.optDouble("gastos"), currency), 14, INK, false));
            panel.addView(text("Balance: " + amount(values.optDouble("balance"), currency), 16, FOREST, true));
        }
        return panel;
    }

    private void showTransactions() {
        installScreen("Movimientos");
        Button add = button("+ Registrar gasto", FOREST);
        pageContent.addView(add);
        add.setOnClickListener(view -> loadCategories(categories -> showTransactionDialog(null, categories)));
        loadTransactionPage(1);
    }

    private void loadTransactionPage(int page) {
        callApi("/transacciones?page=" + page + "&per_page=50", "GET", null, response -> {
            JSONArray items = response.optJSONArray("data");
            if (items == null) return;
            if (page == 1 && items.length() == 0) {
                addText("Aún no hay movimientos.", 14, MUTED, false);
                return;
            }
            for (int i = 0; i < items.length(); i++) {
                JSONObject item = items.optJSONObject(i);
                if (item == null) continue;
                LinearLayout row = card();
                row.addView(text(item.optString("categoria") + " · " + item.optString("fecha"), 14, INK, true));
                row.addView(text(item.optString("tipo") + " · " + amount(item.optDouble("monto"), item.optString("moneda")), 14, TEAL, false));
                row.addView(text(item.optString("descripcion", ""), 13, MUTED, false));
                LinearLayout actions = horizontal();
                Button edit = smallButton("Editar");
                Button delete = smallButton("Eliminar");
                actions.addView(edit);
                actions.addView(delete);
                row.addView(actions);
                pageContent.addView(row);
                edit.setOnClickListener(view -> loadCategories(categories -> showTransactionDialog(item, categories)));
                delete.setOnClickListener(view -> confirmDelete("¿Eliminar este movimiento?", "/transacciones/" + item.optInt("id_transaccion"), this::showTransactions));
            }
            JSONObject pagination = response.optJSONObject("pagination");
            if (pagination != null && pagination.optBoolean("has_next")) {
                Button loadMore = smallButton("Cargar más movimientos");
                pageContent.addView(loadMore);
                loadMore.setOnClickListener(view -> {
                    pageContent.removeView(loadMore);
                    loadTransactionPage(page + 1);
                });
            }
        });
    }

    private void showTransactionDialog(JSONObject current, JSONArray categories) {
        ArrayList<JSONObject> expenses = filterCategories(categories, "GASTO");
        if (expenses.isEmpty()) {
            Toast.makeText(this, "Primero crea una categoría de tipo GASTO.", Toast.LENGTH_LONG).show();
            return;
        }
        LinearLayout form = dialogForm();
        Spinner categorySpinner = spinner(categoryLabels(expenses));
        EditText amountInput = input("Monto", InputType.TYPE_CLASS_NUMBER | InputType.TYPE_NUMBER_FLAG_DECIMAL);
        Spinner currencySpinner = spinner(new String[]{"PEN", "USD"});
        EditText dateInput = input("Fecha YYYY-MM-DD", InputType.TYPE_CLASS_TEXT);
        EditText descriptionInput = input("Descripción", InputType.TYPE_CLASS_TEXT);
        form.addView(categorySpinner);
        form.addView(amountInput);
        form.addView(currencySpinner);
        form.addView(dateInput);
        form.addView(descriptionInput);
        dateInput.setText(current == null ? new SimpleDateFormat("yyyy-MM-dd", Locale.US).format(new Date()) : current.optString("fecha"));
        if (current != null) {
            amountInput.setText(String.valueOf(current.optDouble("monto")));
            descriptionInput.setText(current.optString("descripcion", ""));
            selectCategory(categorySpinner, expenses, current.optInt("id_categoria"));
            currencySpinner.setSelection("USD".equals(current.optString("moneda")) ? 1 : 0);
        }
        AlertDialog dialog = new AlertDialog.Builder(this)
                .setTitle(current == null ? "Registrar gasto" : "Editar movimiento")
                .setView(form)
                .setNegativeButton("Cancelar", null)
                .setPositiveButton("Guardar", null)
                .create();
        dialog.setOnShowListener(ignored -> dialog.getButton(AlertDialog.BUTTON_POSITIVE).setOnClickListener(view -> {
            String amountText = amountInput.getText().toString().trim();
            if (amountText.isEmpty() || categorySpinner.getSelectedItemPosition() < 0) {
                amountInput.setError("Completa el monto y la categoría");
                return;
            }
            JSONObject payload = new JSONObject();
            try {
                payload.put("id_categoria", expenses.get(categorySpinner.getSelectedItemPosition()).optInt("id_categoria"));
                payload.put("tipo", "GASTO");
                payload.put("monto", Double.parseDouble(amountText));
                payload.put("moneda", currencySpinner.getSelectedItem().toString());
                payload.put("fecha", dateInput.getText().toString().trim());
                payload.put("descripcion", descriptionInput.getText().toString().trim());
            } catch (Exception error) {
                amountInput.setError("Monto o fecha no válidos");
                return;
            }
            String path = "/transacciones" + (current == null ? "" : "/" + current.optInt("id_transaccion"));
            callApi(path, current == null ? "POST" : "PUT", payload, response -> {
                dialog.dismiss();
                showTransactions();
            });
        }));
        dialog.show();
    }

    private void showCategories() {
        installScreen("Categorías");
        Button add = button("+ Nueva categoría", FOREST);
        pageContent.addView(add);
        add.setOnClickListener(view -> showCategoryDialog(null));
        loadCategories(categories -> {
            if (categories.length() == 0) {
                addText("Aún no hay categorías.", 14, MUTED, false);
                return;
            }
            for (int i = 0; i < categories.length(); i++) {
                JSONObject item = categories.optJSONObject(i);
                if (item == null) continue;
                LinearLayout row = card();
                row.addView(text(item.optString("nombre"), 16, INK, true));
                row.addView(text(item.optString("tipo") + " · " + item.optString("descripcion", ""), 13, MUTED, false));
                LinearLayout actions = horizontal();
                Button edit = smallButton("Editar");
                Button delete = smallButton("Eliminar");
                actions.addView(edit);
                actions.addView(delete);
                row.addView(actions);
                pageContent.addView(row);
                edit.setOnClickListener(view -> showCategoryDialog(item));
                delete.setOnClickListener(view -> confirmDelete("¿Eliminar esta categoría? Solo se puede si no tiene movimientos ni presupuestos.", "/categorias/" + item.optInt("id_categoria"), this::showCategories));
            }
        });
    }

    private void showCategoryDialog(JSONObject current) {
        LinearLayout form = dialogForm();
        EditText nameInput = input("Nombre", InputType.TYPE_CLASS_TEXT | InputType.TYPE_TEXT_FLAG_CAP_SENTENCES);
        Spinner typeSpinner = spinner(new String[]{"GASTO", "INGRESO"});
        EditText descriptionInput = input("Descripción (opcional)", InputType.TYPE_CLASS_TEXT);
        form.addView(nameInput);
        form.addView(typeSpinner);
        form.addView(descriptionInput);
        if (current != null) {
            nameInput.setText(current.optString("nombre"));
            descriptionInput.setText(current.optString("descripcion", ""));
            typeSpinner.setSelection("INGRESO".equals(current.optString("tipo")) ? 1 : 0);
        }
        AlertDialog dialog = new AlertDialog.Builder(this)
                .setTitle(current == null ? "Nueva categoría" : "Editar categoría")
                .setView(form)
                .setNegativeButton("Cancelar", null)
                .setPositiveButton("Guardar", null)
                .create();
        dialog.setOnShowListener(ignored -> dialog.getButton(AlertDialog.BUTTON_POSITIVE).setOnClickListener(view -> {
            if (nameInput.getText().toString().trim().isEmpty()) {
                nameInput.setError("El nombre es obligatorio");
                return;
            }
            JSONObject payload = new JSONObject();
            try {
                payload.put("nombre", nameInput.getText().toString().trim());
                payload.put("tipo", typeSpinner.getSelectedItem().toString());
                payload.put("descripcion", descriptionInput.getText().toString().trim());
            } catch (Exception error) {
                return;
            }
            String path = "/categorias" + (current == null ? "" : "/" + current.optInt("id_categoria"));
            callApi(path, current == null ? "POST" : "PUT", payload, response -> {
                dialog.dismiss();
                showCategories();
            });
        }));
        dialog.show();
    }

    private void showBudgets() {
        installScreen("Presupuestos");
        Button add = button("+ Nuevo presupuesto", FOREST);
        pageContent.addView(add);
        add.setOnClickListener(view -> loadCategories(categories -> showBudgetDialog(null, categories)));
        String[] period = getPeriod();
        callApi("/presupuestos/seguimiento?mes=" + period[0] + "&anio=" + period[1], "GET", null, response -> {
            JSONArray items = response.optJSONArray("data");
            if (items == null || items.length() == 0) {
                addText("No hay presupuestos para este periodo.", 14, MUTED, false);
                return;
            }
            for (int i = 0; i < items.length(); i++) {
                JSONObject item = items.optJSONObject(i);
                if (item == null) continue;
                LinearLayout row = card();
                row.addView(text(item.optString("categoria") + " · " + item.optString("moneda"), 16, INK, true));
                row.addView(text(amount(item.optDouble("gasto_acumulado"), item.optString("moneda")) + " de " + amount(item.optDouble("monto_limite"), item.optString("moneda")), 14, TEAL, false));
                row.addView(text(item.optDouble("porcentaje_consumido") + "% · " + item.optString("estado"), 13, MUTED, false));
                row.addView(text("Disponible: " + amount(item.optDouble("saldo_disponible"), item.optString("moneda")), 13, INK, false));
                LinearLayout actions = horizontal();
                Button edit = smallButton("Editar");
                Button delete = smallButton("Eliminar");
                actions.addView(edit);
                actions.addView(delete);
                row.addView(actions);
                pageContent.addView(row);
                edit.setOnClickListener(view -> loadCategories(categories -> showBudgetDialog(item, categories)));
                delete.setOnClickListener(view -> confirmDelete("¿Eliminar este presupuesto?", "/presupuestos/" + item.optInt("id_presupuesto"), this::showBudgets));
            }
        });
    }

    private void showBudgetDialog(JSONObject current, JSONArray categories) {
        ArrayList<JSONObject> expenses = filterCategories(categories, "GASTO");
        if (expenses.isEmpty()) {
            Toast.makeText(this, "Primero crea una categoría de tipo GASTO.", Toast.LENGTH_LONG).show();
            return;
        }
        LinearLayout form = dialogForm();
        Spinner categorySpinner = spinner(categoryLabels(expenses));
        EditText amountInput = input("Monto límite", InputType.TYPE_CLASS_NUMBER | InputType.TYPE_NUMBER_FLAG_DECIMAL);
        Spinner currencySpinner = spinner(new String[]{"PEN", "USD"});
        String[] currentPeriod = getPeriod();
        EditText monthInput = input("Mes (1-12)", InputType.TYPE_CLASS_NUMBER);
        EditText yearInput = input("Año", InputType.TYPE_CLASS_NUMBER);
        form.addView(categorySpinner);
        form.addView(amountInput);
        form.addView(currencySpinner);
        form.addView(monthInput);
        form.addView(yearInput);
        monthInput.setText(current == null ? currentPeriod[0] : String.valueOf(current.optInt("mes")));
        yearInput.setText(current == null ? currentPeriod[1] : String.valueOf(current.optInt("anio")));
        if (current != null) {
            amountInput.setText(String.valueOf(current.optDouble("monto_limite")));
            selectCategory(categorySpinner, expenses, current.optInt("id_categoria"));
            currencySpinner.setSelection("USD".equals(current.optString("moneda")) ? 1 : 0);
        }
        AlertDialog dialog = new AlertDialog.Builder(this)
                .setTitle(current == null ? "Nuevo presupuesto" : "Editar presupuesto")
                .setView(form)
                .setNegativeButton("Cancelar", null)
                .setPositiveButton("Guardar", null)
                .create();
        dialog.setOnShowListener(ignored -> dialog.getButton(AlertDialog.BUTTON_POSITIVE).setOnClickListener(view -> {
            try {
                JSONObject payload = new JSONObject()
                        .put("id_categoria", expenses.get(categorySpinner.getSelectedItemPosition()).optInt("id_categoria"))
                        .put("monto_limite", Double.parseDouble(amountInput.getText().toString().trim()))
                        .put("moneda", currencySpinner.getSelectedItem().toString())
                        .put("mes", Integer.parseInt(monthInput.getText().toString().trim()))
                        .put("anio", Integer.parseInt(yearInput.getText().toString().trim()));
                String path = "/presupuestos" + (current == null ? "" : "/" + current.optInt("id_presupuesto"));
                callApi(path, current == null ? "POST" : "PUT", payload, response -> {
                    dialog.dismiss();
                    showBudgets();
                });
            } catch (Exception error) {
                amountInput.setError("Completa monto, mes y año correctamente");
            }
        }));
        dialog.show();
    }

    private void showReports() {
        installScreen("Reportes");
        String[] period = getPeriod();
        callApi("/reportes/resumen?mes=" + period[0] + "&anio=" + period[1], "GET", null, response -> {
            JSONObject data = response.optJSONObject("data");
            if (data == null) return;
            pageContent.addView(currencyPanel("PEN", data.optJSONObject("PEN")));
            pageContent.addView(currencyPanel("USD", data.optJSONObject("USD")));
            addText("Gastos por categoría", 18, INK, true);
            callApi("/reportes/gastos-categoria?mes=" + period[0] + "&anio=" + period[1], "GET", null, expensesResponse -> {
                JSONArray expenses = expensesResponse.optJSONArray("data");
                if (expenses != null) {
                    for (int i = 0; i < expenses.length(); i++) {
                        JSONObject item = expenses.optJSONObject(i);
                        if (item != null) addText(item.optString("categoria") + " · " + amount(item.optDouble("total"), item.optString("moneda")), 14, MUTED, false);
                    }
                }
                addText("Evolución anual", 18, INK, true);
                callApi("/reportes/evolucion?anio=" + period[1], "GET", null, evolutionResponse -> {
                    JSONObject evolution = evolutionResponse.optJSONObject("data");
                    JSONArray months = evolution == null ? null : evolution.optJSONArray("meses");
                    if (months != null) {
                        for (int i = 0; i < months.length(); i++) {
                            JSONObject month = months.optJSONObject(i);
                            if (month == null) continue;
                            JSONObject pen = month.optJSONObject("PEN");
                            JSONObject usd = month.optJSONObject("USD");
                            addText("Mes " + month.optInt("mes") + " · PEN ingresos " + amount(pen.optDouble("ingresos"), "PEN")
                                    + ", gastos " + amount(pen.optDouble("gastos"), "PEN")
                                    + " · USD ingresos " + amount(usd.optDouble("ingresos"), "USD")
                                    + ", gastos " + amount(usd.optDouble("gastos"), "USD"), 12, MUTED, false);
                        }
                    }
                });
            });
        });
    }

    private void loadCategories(java.util.function.Consumer<JSONArray> result) {
        callApi("/categorias", "GET", null, response -> {
            JSONArray items = response.optJSONArray("data");
            result.accept(items == null ? new JSONArray() : items);
        });
    }

    private void confirmDelete(String message, String path, Runnable refresh) {
        new AlertDialog.Builder(this)
                .setMessage(message)
                .setNegativeButton("Cancelar", null)
                .setPositiveButton("Eliminar", (dialog, which) -> callApi(path, "DELETE", null, response -> {
                    Toast.makeText(this, "Registro eliminado.", Toast.LENGTH_SHORT).show();
                    refresh.run();
                }))
                .show();
    }

    private void installScreen(String title) {
        LinearLayout root = baseColumn();
        root.setPadding(dp(16), dp(18), dp(16), dp(12));
        LinearLayout header = horizontal();
        TextView heading = text("FINTRACK · " + title, 22, FOREST, true);
        header.addView(heading, new LinearLayout.LayoutParams(0, -2, 1));
        Button logout = smallButton("Salir");
        if (isDebugBuild()) {
            Button server = smallButton("Servidor");
            header.addView(server);
            server.setOnClickListener(view -> showApiConfigDialog());
        }
        header.addView(logout);
        root.addView(header);
        logout.setOnClickListener(view -> {
            String sessionToken = token;
            String serverUrl = apiBase;
            clearSession();
            showLogin();
            executor.execute(() -> {
                try {
                    ApiClient.request(serverUrl, "/auth/logout", "POST", sessionToken, null);
                } catch (Exception error) {
                    runOnUiThread(() -> Toast.makeText(
                            this,
                            "Sesión cerrada en este dispositivo; no se pudo revocar en el servidor.",
                            Toast.LENGTH_LONG
                    ).show());
                }
            });
        });

        HorizontalScrollView navScroll = new HorizontalScrollView(this);
        LinearLayout nav = horizontal();
        addNavButton(nav, "Resumen", this::showDashboard);
        addNavButton(nav, "Movimientos", this::showTransactions);
        addNavButton(nav, "Categorías", this::showCategories);
        addNavButton(nav, "Presupuestos", this::showBudgets);
        addNavButton(nav, "Reportes", this::showReports);
        navScroll.addView(nav);
        root.addView(navScroll);

        ScrollView scroll = new ScrollView(this);
        pageContent = baseColumn();
        pageContent.setPadding(0, dp(12), 0, dp(20));
        scroll.addView(pageContent);
        root.addView(scroll, new LinearLayout.LayoutParams(-1, 0, 1));
        setContentView(root);
    }

    private void showApiConfigDialog() {
        LinearLayout form = dialogForm();
        EditText urlInput = input("https://tu-dominio/api", InputType.TYPE_CLASS_TEXT | InputType.TYPE_TEXT_VARIATION_URI);
        urlInput.setText(apiBase);
        form.addView(urlInput);
        AlertDialog dialog = new AlertDialog.Builder(this)
                .setTitle("Servidor FINTRACK")
                .setMessage("Producción: usa la URL HTTPS de la API. HTTP solo funciona en builds debug. Al cambiar de servidor, vuelve a iniciar sesión.")
                .setView(form)
                .setNegativeButton("Cancelar", null)
                .setPositiveButton("Guardar", null)
                .create();
        dialog.setOnShowListener(ignored -> dialog.getButton(AlertDialog.BUTTON_POSITIVE).setOnClickListener(view -> {
            if (!applyApiBase(urlInput, null)) return;
            clearSession();
            dialog.dismiss();
            showLogin();
        }));
        dialog.show();
    }

    private void addNavButton(LinearLayout nav, String label, Runnable action) {
        Button button = smallButton(label);
        nav.addView(button);
        button.setOnClickListener(view -> action.run());
    }

    private void addText(String value, int size, int color, boolean bold) {
        TextView view = text(value, size, color, bold);
        view.setPadding(dp(4), dp(8), dp(4), dp(8));
        pageContent.addView(view);
    }

    private LinearLayout baseColumn() {
        LinearLayout layout = new LinearLayout(this);
        layout.setOrientation(LinearLayout.VERTICAL);
        layout.setBackgroundColor(CANVAS);
        return layout;
    }

    private LinearLayout horizontal() {
        LinearLayout layout = new LinearLayout(this);
        layout.setOrientation(LinearLayout.HORIZONTAL);
        layout.setGravity(Gravity.CENTER_VERTICAL);
        return layout;
    }

    private LinearLayout card() {
        LinearLayout layout = baseColumn();
        layout.setPadding(dp(14), dp(12), dp(14), dp(12));
        layout.setBackgroundColor(WHITE);
        LinearLayout.LayoutParams params = new LinearLayout.LayoutParams(-1, -2);
        params.setMargins(0, dp(6), 0, dp(6));
        layout.setLayoutParams(params);
        return layout;
    }

    private TextView text(String value, int size, int color, boolean bold) {
        TextView view = new TextView(this);
        view.setText(value);
        view.setTextSize(size);
        view.setTextColor(color);
        if (bold) view.setTypeface(null, android.graphics.Typeface.BOLD);
        return view;
    }

    private EditText input(String hint, int inputType) {
        EditText view = new EditText(this);
        view.setSingleLine(true);
        view.setHint(hint);
        view.setInputType(inputType);
        view.setTextSize(15);
        view.setTextColor(INK);
        view.setHintTextColor(MUTED);
        view.setPadding(dp(12), dp(9), dp(12), dp(9));
        LinearLayout.LayoutParams params = new LinearLayout.LayoutParams(-1, -2);
        params.setMargins(0, dp(5), 0, dp(5));
        view.setLayoutParams(params);
        return view;
    }

    private Button button(String label, int color) {
        Button button = new Button(this);
        button.setText(label);
        button.setTextColor(WHITE);
        button.setTextSize(14);
        button.setAllCaps(false);
        button.setBackgroundTintList(android.content.res.ColorStateList.valueOf(color));
        LinearLayout.LayoutParams params = new LinearLayout.LayoutParams(-1, -2);
        params.setMargins(0, dp(5), 0, dp(5));
        button.setLayoutParams(params);
        return button;
    }

    private Button smallButton(String label) {
        Button button = new Button(this);
        button.setText(label);
        button.setTextSize(12);
        button.setAllCaps(false);
        button.setTextColor(FOREST);
        button.setBackgroundTintList(android.content.res.ColorStateList.valueOf(0xFFE1ECE5));
        return button;
    }

    private Spinner spinner(String[] values) {
        Spinner spinner = new Spinner(this);
        ArrayAdapter<String> adapter = new ArrayAdapter<>(this, android.R.layout.simple_spinner_item, values);
        adapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
        spinner.setAdapter(adapter);
        return spinner;
    }

    private LinearLayout dialogForm() {
        LinearLayout form = baseColumn();
        form.setPadding(dp(18), dp(8), dp(18), dp(4));
        return form;
    }

    private ArrayList<JSONObject> filterCategories(JSONArray source, String type) {
        ArrayList<JSONObject> result = new ArrayList<>();
        for (int i = 0; i < source.length(); i++) {
            JSONObject item = source.optJSONObject(i);
            if (item != null && type.equals(item.optString("tipo"))) result.add(item);
        }
        return result;
    }

    private String[] categoryLabels(ArrayList<JSONObject> categories) {
        String[] labels = new String[categories.size()];
        for (int i = 0; i < categories.size(); i++) labels[i] = categories.get(i).optString("nombre");
        return labels;
    }

    private void selectCategory(Spinner spinner, ArrayList<JSONObject> categories, int categoryId) {
        for (int i = 0; i < categories.size(); i++) {
            if (categories.get(i).optInt("id_categoria") == categoryId) {
                spinner.setSelection(i);
                return;
            }
        }
    }

    private String[] getPeriod() {
        String current = periodField == null ? "" : periodField.getText().toString().trim();
        if (!current.matches("\\d{4}-\\d{2}")) current = new SimpleDateFormat("yyyy-MM", Locale.US).format(new Date());
        String[] parts = current.split("-");
        return new String[]{String.valueOf(Integer.parseInt(parts[1])), parts[0]};
    }

    private String amount(double value, String currency) {
        return ("PEN".equals(currency) ? "S/ " : "$ ") + String.format(Locale.US, "%.2f", value);
    }

    private int dp(int value) {
        return Math.round(value * getResources().getDisplayMetrics().density);
    }

    private void saveApiBase() {
        preferences.edit().putString("api_base", apiBase).apply();
    }

    private boolean applyApiBase(EditText input, TextView message) {
        String value = input.getText().toString().trim().replaceAll("/+$", "");
        boolean usesHttps = value.startsWith("https://");
        boolean allowsDebugHttp = isDebugBuild() && value.startsWith("http://");
        int schemeEnd = value.indexOf("://") + 3;
        int apiPath = value.lastIndexOf("/api");
        if ((!usesHttps && !allowsDebugHttp)
                || apiPath <= schemeEnd
                || !value.endsWith("/api")
                || value.substring(schemeEnd, apiPath).contains("/")) {
            String error = "Usa una URL HTTPS que termine en /api. HTTP solo está permitido en debug.";
            if (message == null) input.setError(error);
            else message.setText(error);
            return false;
        }
        apiBase = value;
        saveApiBase();
        return true;
    }

    private boolean isDebugBuild() {
        return (getApplicationInfo().flags
                & android.content.pm.ApplicationInfo.FLAG_DEBUGGABLE) != 0;
    }

    private void clearSession() {
        token = "";
        userName = "";
        preferences.edit().remove("access_token").apply();
    }
}