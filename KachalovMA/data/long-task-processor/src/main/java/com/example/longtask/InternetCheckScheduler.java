package com.example.longtask;

import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

import java.net.HttpURLConnection;
import java.net.URI;
import java.time.LocalDateTime;

@Component
public class InternetCheckScheduler {

    private static final String CHECK_URL = "https://clients3.google.com/generate_204";

    @Scheduled(fixedDelay = 30_000, initialDelay = 2_000)
    public void checkInternet() {
        try {
            HttpURLConnection connection = (HttpURLConnection) URI.create(CHECK_URL).toURL().openConnection();
            connection.setRequestMethod("GET");
            connection.setConnectTimeout(5_000);
            connection.setReadTimeout(5_000);

            int statusCode = connection.getResponseCode();
            boolean internetAvailable = statusCode == 204;

            System.out.println(LocalDateTime.now()
                    + " internetAvailable="
                    + internetAvailable
                    + " statusCode="
                    + statusCode);
        } catch (Exception exception) {
            System.out.println(LocalDateTime.now()
                    + " internetAvailable=false error="
                    + exception.getMessage());
        }
    }
}
