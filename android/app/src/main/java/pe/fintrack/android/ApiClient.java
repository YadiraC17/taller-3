package pe.fintrack.android;

import org.json.JSONException;
import org.json.JSONObject;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;

public final class ApiClient {
    private ApiClient() { }

    public static final class HttpError extends IOException {
        public final int statusCode;

        HttpError(int statusCode, String message) {
            super(message);
            this.statusCode = statusCode;
        }
    }

    public static JSONObject request(String baseUrl, String path, String method, String token, JSONObject body)
            throws IOException, JSONException {
        String normalizedBase = baseUrl.trim().replaceAll("/+$", "");
        HttpURLConnection connection = (HttpURLConnection) new URL(normalizedBase + path).openConnection();
        connection.setRequestMethod(method);
        connection.setConnectTimeout(12000);
        connection.setReadTimeout(15000);
        connection.setRequestProperty("Accept", "application/json");
        if (token != null && !token.isEmpty()) {
            connection.setRequestProperty("Authorization", "Bearer " + token);
        }
        if (body != null) {
            connection.setRequestProperty("Content-Type", "application/json; charset=utf-8");
            connection.setDoOutput(true);
            try (OutputStream output = connection.getOutputStream()) {
                output.write(body.toString().getBytes(StandardCharsets.UTF_8));
            }
        }

        int status = connection.getResponseCode();
        if (status == HttpURLConnection.HTTP_NO_CONTENT) {
            connection.disconnect();
            return new JSONObject().put("success", true).put("data", JSONObject.NULL);
        }
        InputStream stream = status >= 200 && status < 300
                ? connection.getInputStream()
                : connection.getErrorStream();
        String responseText = readBody(stream);
        connection.disconnect();

        JSONObject response = responseText.isEmpty() ? new JSONObject() : new JSONObject(responseText);
        if (status < 200 || status >= 300 || !response.optBoolean("success", true)) {
            throw new HttpError(status, response.optString("message", "Error HTTP " + status));
        }
        return response;
    }

    private static String readBody(InputStream stream) throws IOException {
        if (stream == null) return "";
        StringBuilder text = new StringBuilder();
        try (BufferedReader reader = new BufferedReader(new InputStreamReader(stream, StandardCharsets.UTF_8))) {
            String line;
            while ((line = reader.readLine()) != null) text.append(line);
        }
        return text.toString();
    }
}