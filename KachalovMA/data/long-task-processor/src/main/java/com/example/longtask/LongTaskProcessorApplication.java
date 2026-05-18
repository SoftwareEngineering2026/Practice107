package com.example.longtask;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.scheduling.annotation.EnableScheduling;

@EnableScheduling
@SpringBootApplication
public class LongTaskProcessorApplication {
    public static void main(String[] args) {
        SpringApplication.run(LongTaskProcessorApplication.class, args);
    }
}
