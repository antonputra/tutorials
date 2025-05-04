package com.antonputra.demo;

import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.bind.annotation.GetMapping;

import io.micrometer.core.instrument.Counter;
import io.micrometer.core.instrument.MeterRegistry;

@RestController
public class DevicesController {

    Counter visitCounter;

    public DevicesController(MeterRegistry registry) {
        visitCounter = Counter.builder("javaapp_devices_total")
                .description("Number of devices calls")
                .register(registry);
    }

    @GetMapping("/api/devices")
    public Device[] getDevices() {
        Device[] devices = {
                new Device("b0e42fe7-31a5-4894-a441-007e5256afea", "5F-33-CC-1F-43-82", "2.1.6"),
                new Device("0c3242f5-ae1f-4e0c-a31b-5ec93825b3e7", "EF-2B-C4-F5-D6-34", "2.1.5"),
                new Device("8c7d519a-38fe-4b7c-946a-a3a88e8fda0e", "FB-0F-1A-F9-8D-04", "2.1.5"),
                new Device("e64cf5c4-2a54-4267-84ab-5eafb0708e89", "4D-B3-E9-15-34-1F", "2.1.5"),
                new Device("bd1a945a-e519-442c-a305-63337519deba", "10-03-06-13-10-59", "2.1.2"),
                new Device("caa0b9c7-33bb-472d-8528-b8dbc569019c", "2B-10-1C-5E-57-54", "2.1.1"),
                new Device("f0771aa5-9ce2-4d92-a8fa-dd9ea00fe6ab", "4C-60-54-D5-A4-7F", "2.1.6"),
                new Device("4d3e4528-5c38-4723-baa9-68b8a27ad214", "9B-15-0F-F7-60-CC", "2.1.4"),
                new Device("67abf1f9-983c-4559-801f-cee90c03b768", "48-1D-BC-54-69-64", "2.2.0"),
                new Device("21ff6a61-118c-4cf1-86ce-cd6659be81a5", "8C-53-F2-A1-69-93", "2.2.0"),
        };
        visitCounter.increment();

        return devices;
    }
}
