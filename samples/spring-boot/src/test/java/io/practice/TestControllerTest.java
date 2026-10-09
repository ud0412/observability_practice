package io.practice;

import com.sun.net.httpserver.HttpServer;
import java.net.InetSocketAddress;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.assertEquals;

class TestControllerTest {
    private void check(int downstreamStatus, long delay, long timeout, int expected) throws Exception {
        HttpServer server = HttpServer.create(new InetSocketAddress("127.0.0.1", 0), 0);
        server.createContext("/test", exchange -> {
            try { Thread.sleep(delay); } catch (InterruptedException error) { Thread.currentThread().interrupt(); }
            byte[] body = "{\"ok\":true}".getBytes();
            try { exchange.sendResponseHeaders(downstreamStatus, body.length); exchange.getResponseBody().write(body); }
            finally { exchange.close(); }
        });
        server.start();
        try {
            var controller = new TestController("http://127.0.0.1:" + server.getAddress().getPort() + "/test", timeout);
            assertEquals(expected, controller.test().getStatusCode().value());
        } finally { server.stop(0); }
    }
    @Test void success() throws Exception { check(200, 0, 1000, 200); }
    @Test void downstreamError() throws Exception { check(500, 0, 1000, 502); }
    @Test void timeout() throws Exception { check(200, 300, 100, 504); }
}
