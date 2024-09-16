const std = @import("std");
const httpz = @import("httpz");
const Device = @import("device.zig");

const port = 8080;

pub fn main() !void {
    var gpa = std.heap.GeneralPurposeAllocator(.{}){};
    const allocator = gpa.allocator();

    var app = App{};

    // playing around with fine tuning params to match what the prod system looks like
    // with is 2 vCPUs ?
    //
    // This should consume around 2MB memory in total for sustained hits
    var server = try httpz.Server(*App).init(allocator, .{
        .address = "0.0.0.0",
        .port = port,
        .workers = .{
            .large_buffer_count = 1,
            .large_buffer_size = 1024,
        },
        .thread_pool = .{
            .count = 1,
            .buffer_size = 1024,
        },
        .request = .{
            .buffer_size = 1024,
            .max_header_count = 0,
            .max_param_count = 0,
            .max_query_count = 0,
            .max_form_count = 0,
            .max_multiform_count = 0,
        },
    }, &app);
    var router = server.router(.{});
    router.get("/healthz", App.healthz, .{});
    router.get("/api/devices", App.getDevices, .{});

    std.debug.print("http.zig listening on http://0.0.0.0:{d}\n", .{port});
    try server.listen();
}

const App = struct {
    fn healthz(_: *App, _: *httpz.Request, res: *httpz.Response) !void {
        res.body = "OK";
    }

    fn getDevices(_: *App, _: *httpz.Request, res: *httpz.Response) !void {
        try res.json([_]Device{Device{
            .id = 1,
            .mac = "EF-2B-C4-F5-D6-34",
            .firmware = "2.1.5",
        }}, .{});
    }
};
