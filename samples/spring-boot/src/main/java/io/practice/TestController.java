package io.practice;

import java.io.IOException;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.net.http.HttpTimeoutException;
import java.time.Duration;
import java.util.Map;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class TestController {
    private static final Logger log = LoggerFactory.getLogger(TestController.class);
    private final HttpClient client;
    private final URI downstream;
    private final Duration responseTimeout;

    public TestController(@Value("${downstream.url}") String url,
                          @Value("${downstream.timeout-ms:3000}") long timeoutMs) {
        this.client = HttpClient.newBuilder().connectTimeout(Duration.ofSeconds(1)).build();
        this.downstream = URI.create(url);
        this.responseTimeout = Duration.ofMillis(timeoutMs);
    }

    @GetMapping("/test")
    public ResponseEntity<?> test() {
        log.info("test request started");
        try {
            HttpRequest request = HttpRequest.newBuilder(downstream).timeout(responseTimeout).GET().build();
            HttpResponse<String> response = client.send(request, HttpResponse.BodyHandlers.ofString());
            log.info("downstream completed status={}", response.statusCode());
            if (response.statusCode() >= 400) {
                log.error("test request failed: downstream HTTP {}", response.statusCode());
                return ResponseEntity.status(502).body(Map.of("error", "downstream_error", "status", response.statusCode()));
            }
            log.info("test request completed");
            return ResponseEntity.ok(Map.of("service", "sample-spring-boot", "downstream", response.body()));
        } catch (HttpTimeoutException error) {
            log.error("downstream timeout", error);
            return ResponseEntity.status(504).body(Map.of("error", "downstream_timeout"));
        } catch (InterruptedException error) {
            Thread.currentThread().interrupt();
            log.error("downstream interrupted", error);
            return ResponseEntity.status(503).body(Map.of("error", "interrupted"));
        } catch (IOException error) {
            log.error("downstream connection failed", error);
            return ResponseEntity.status(502).body(Map.of("error", "downstream_unavailable"));
        }
    }

    @GetMapping("/health")
    public Map<String, String> health() { return Map.of("status", "ok"); }
}
