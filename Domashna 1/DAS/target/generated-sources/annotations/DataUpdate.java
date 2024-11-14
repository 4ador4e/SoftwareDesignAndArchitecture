import java.io.*;
import java.net.HttpURLConnection;
import java.net.URL;
import java.text.SimpleDateFormat;
import java.util.*;
import com.opencsv.CSVReader;
import com.opencsv.CSVWriter;
import org.json.JSONArray;
import org.json.JSONObject;

public class DataUpdate {
    public static List<Map<String, Object>> fetchMissingData(String issuerCode, String lastDate) throws Exception {
        String urlStr = String.format("https://www.mse.mk/mk/stats/symbolhistory/",
                issuerCode, lastDate, new SimpleDateFormat("yyyy-MM-dd").format(new Date()));
        URL url = new URL(urlStr);
        HttpURLConnection conn = (HttpURLConnection) url.openConnection();
        conn.setRequestMethod("GET");

        BufferedReader in = new BufferedReader(new InputStreamReader(conn.getInputStream()));
        String inputLine;
        StringBuilder content = new StringBuilder();
        while ((inputLine = in.readLine()) != null) {
            content.append(inputLine);
        }

        in.close();
        conn.disconnect();

        List<Map<String, Object>> result = new ArrayList<>();


        JSONArray jsonArray = new JSONArray(content.toString());
        for (int i = 0; i < jsonArray.length(); i++) {
            JSONObject jsonObj = jsonArray.getJSONObject(i);
            Map<String, Object> record = new HashMap<>();
            record.put("date", jsonObj.getString("date"));
            record.put("price", jsonObj.get("price"));
            result.add(record);
        }

        return result;
    }

    public static Map<String, String> getLastDatesFromCSV(String filePath) throws Exception {
        Map<String, String> lastDates = new HashMap<>();

        try (CSVReader reader = new CSVReader(new FileReader(filePath))) {
            String[] line;
            while ((line = reader.readNext()) != null) {
                String code = line[0];
                String date = line[1];
                lastDates.put(code, date);
            }
        }

        return lastDates;
    }

    public static void updateCSVWithNewData(String filePath, Map<String, String> lastDates) throws Exception {
        List<String[]> updatedRows = new ArrayList<>();

        for (Map.Entry<String, String> entry : lastDates.entrySet()) {
            String issuerCode = entry.getKey();
            String lastDate = entry.getValue();


            try {
                List<Map<String, Object>> newData = fetchMissingData(issuerCode, lastDate);

                for (Map<String, Object> record : newData) {
                    String date = record.get("date").toString();
                    String price = record.get("price").toString();
                    updatedRows.add(new String[]{issuerCode, date, price});
                }
            } catch (Exception e) {
                System.err.println("Error fetching data for issuer: " + issuerCode + ", last date: " + lastDate);
                e.printStackTrace();
            }
        }


        try (CSVWriter writer = new CSVWriter(new FileWriter(filePath, true))) {
            writer.writeAll(updatedRows);
        } catch (IOException e) {
            System.err.println("Error writing to CSV file.");
            e.printStackTrace();
        }
    }

    public static void main(String[] args) throws Exception {
        String filePath = "C:\\Users\\Eva\\IdeaProjects\\DAS\\Sevkupno.csv";


        Map<String, String> lastDates = getLastDatesFromCSV(filePath);


        updateCSVWithNewData(filePath, lastDates);

        System.out.println("CSV file updated successfully.");
    }
}

