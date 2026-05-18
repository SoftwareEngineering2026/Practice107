package com.example.backend;

import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;
import java.util.UUID;
import java.util.concurrent.atomic.AtomicLong;

@RestController
@CrossOrigin(origins = "*")
public class UuidController {

    private final AtomicLong uuidRequestsTotal = new AtomicLong();

    @GetMapping("/api/uuid")
    public Map<String, String> generateUuid() {
        long total = uuidRequestsTotal.incrementAndGet();
        System.out.println("uuid_generated total=" + total);
        return Map.of("uuid", UUID.randomUUID().toString());
    }

    @GetMapping(value = "/metrics", produces = MediaType.TEXT_PLAIN_VALUE)
    public String metrics() {
        return "# HELP uuid_requests_total Total UUID generation requests\n"
                + "# TYPE uuid_requests_total counter\n"
                + "uuid_requests_total " + uuidRequestsTotal.get() + "\n";
    }
}
